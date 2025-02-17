import json
from typing import List, Set

from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from pyre_extensions import none_throws

from backend.common.cache_clearing import get_affected_queries
from backend.common.manipulators.manipulator_base import ManipulatorBase, TUpdatedModel
from backend.common.models.award import Award
from backend.common.models.cached_model import TAffectedReferences


class AwardManipulator(ManipulatorBase[Award]):
    """
    Handle Award database writes.
    """

    @classmethod
    def getCacheKeysAndQueries(
        cls, affected_refs: TAffectedReferences
    ) -> List[get_affected_queries.TCacheKeyAndQuery]:
        return get_affected_queries.award_updated(affected_refs)

    @classmethod
    def updateMerge(
        cls, new_model: Award, old_model: Award, auto_union: bool = True
    ) -> Award:
        auto_union_list_attrs = {
            "team_list",
            "recipient_json_list",
        }

        json_list_attrs = {"recipient_json_list"}

        cls._update_attrs(new_model, old_model, auto_union)

        for attr in auto_union_list_attrs:
            # JSON equaltiy comparison is not deterministic
            if attr in json_list_attrs:
                old_list = [json.loads(j) for j in getattr(old_model, attr)]
                new_list = [json.loads(j) for j in getattr(new_model, attr)]
            else:
                old_list = getattr(old_model, attr)
                new_list = getattr(new_model, attr)

            if auto_union:
                for item in new_list:
                    if item not in old_list:
                        old_list.append(item)
                        old_model._dirty = True
            else:
                old_list = new_list

            # Turn dicts back to JSON
            if attr in json_list_attrs:
                merged_list = [json.dumps(d) for d in old_list]
            else:
                merged_list = old_list

            setattr(old_model, attr, merged_list)

        return old_model


@AwardManipulator.register_post_update_hook
def award_post_update_hook(updated_models: List[TUpdatedModel[Award]]) -> None:
    event_keys: Set[ndb.Key] = set()
    for updated_award in updated_models:
        event_keys.add(none_throws(updated_award.model.event))

    for event_key in event_keys:
        # Enqueue task to calculate district points
        taskqueue.add(
            url=f"/tasks/math/do/district_points_calc/{event_key.string_id()}",
            method="GET",
            target="py3-tasks-io",
            queue_name="default",
        )


"""
    @classmethod
    def postUpdateHook(cls, awards, updated_attr_list, is_new_list):
        # Note, updated_attr_list will always be empty, for now
        # Still needs to be implemented in updateMerge
        # See helpers.EventManipulator
        events = []
        for (award, updated_attrs) in zip(awards, updated_attr_list):
            event = award.event
            if event not in events:
                events.append(event)

        for event in events:
            if event.get().within_a_day:
                try:
                    NotificationHelper.send_award_update(event.get())
                except Exception:
                    logging.error("Error sending award update for {}".format(event.id()))
                try:
                    TBANSHelper.awards(event.get())
                except Exception, exception:
                    logging.error("Error sending {} award updates: {}".format(event.id(), exception))
                    logging.error(traceback.format_exc())
"""
