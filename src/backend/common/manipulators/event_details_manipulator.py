import logging
from typing import List

from google.appengine.api import taskqueue

from backend.common.cache_clearing import get_affected_queries
from backend.common.manipulators.manipulator_base import ManipulatorBase, TUpdatedModel
from backend.common.models.cached_model import TAffectedReferences
from backend.common.models.event_details import EventDetails


class EventDetailsManipulator(ManipulatorBase[EventDetails]):
    """
    Handle EventDetails database writes.
    """

    @classmethod
    def getCacheKeysAndQueries(
        cls, affected_refs: TAffectedReferences
    ) -> List[get_affected_queries.TCacheKeyAndQuery]:
        return get_affected_queries.event_details_updated(affected_refs)

    @classmethod
    def updateMerge(
        cls,
        new_model: EventDetails,
        old_model: EventDetails,
        auto_union: bool = True,
    ) -> EventDetails:
        cls._update_attrs(new_model, old_model, auto_union)
        return old_model


@EventDetailsManipulator.register_post_update_hook
def event_details_post_update_hook(
    updated_models: List[TUpdatedModel[EventDetails]],
) -> None:
    for updated_model in updated_models:
        # Enqueue task to calculate district points
        event_key = updated_model.model.key_name
        try:
            taskqueue.add(
                url=f"/tasks/math/do/district_points_calc/{event_key}",
                method="GET",
                target="py3-tasks-io",
                queue_name="default",
            )
        except Exception:
            logging.exception(f"Error enqueuing district_points_calc for {event_key}")

        # Enqueue task to calculate event team status
        try:
            taskqueue.add(
                url=f"/tasks/math/do/event_team_status/{event_key}",
                method="GET",
                target="py3-tasks-io",
                queue_name="default",
            )
        except Exception:
            logging.exception(f"Error enqueuing event_team_status for {event_key}")


"""ndb
    @classmethod
    def postUpdateHook(cls, event_details_list, updated_attr_list, is_new_list):
        '''
        To run after models have been updated
        '''
        for (event_details, updated_attrs) in zip(event_details_list, updated_attr_list):
            event = Event.get_by_id(event_details.key.id())
            if event.within_a_day and "alliance_selections" in updated_attrs:
                try:
                    NotificationHelper.send_alliance_update(event)
                except Exception:
                    logging.error("Error sending alliance update notification for {}".format(event.key_name))
                    logging.error(traceback.format_exc())
                try:
                    TBANSHelper.alliance_selection(event)
                except Exception:
                    logging.error("Error sending alliance update notification for {}".format(event.key_name))
                    logging.error(traceback.format_exc())

            try:
                FirebasePusher.update_event_details(event_details)
            except Exception:
                logging.warning("Firebase update_event_details failed!")
"""
