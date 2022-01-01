import re
from typing import List, Optional, Set

from flask import (
    Blueprint,
    escape,
    make_response,
    render_template,
    request,
    Response,
    url_for,
)
from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from pyre_extensions import none_throws, safe_cast

from backend.common.helpers.event_helper import EventHelper
from backend.common.helpers.event_remapteams_helper import EventRemapTeamsHelper
from backend.common.helpers.listify import listify
from backend.common.helpers.offseason_event_helper import OffseasonEventHelper
from backend.common.helpers.season_helper import SeasonHelper
from backend.common.manipulators.award_manipulator import AwardManipulator
from backend.common.manipulators.district_manipulator import DistrictManipulator
from backend.common.manipulators.district_team_manipulator import (
    DistrictTeamManipulator,
)
from backend.common.manipulators.event_manipulator import EventManipulator
from backend.common.manipulators.event_team_manipulator import EventTeamManipulator
from backend.common.manipulators.media_manipulator import MediaManipulator
from backend.common.manipulators.robot_manipulator import RobotManipulator
from backend.common.manipulators.team_manipulator import TeamManipulator
from backend.common.models.district_team import DistrictTeam
from backend.common.models.event import Event
from backend.common.models.event_team import EventTeam
from backend.common.models.keys import EventKey, TeamKey, Year
from backend.common.models.robot import Robot
from backend.common.models.team import Team
from backend.common.sitevars.apistatus import ApiStatus
from backend.common.sitevars.cmp_registration_hacks import ChampsRegistrationHacks
from backend.common.suggestions.suggestion_creator import SuggestionCreator
from backend.tasks_io.datafeeds.datafeed_fms_api import DatafeedFMSAPI


blueprint = Blueprint("frc_api", __name__)


@blueprint.route("/backend-tasks/enqueue/event_list/current", defaults={"year": None})
@blueprint.route("/backend-tasks/enqueue/event_list/<int:year>")
def enqueue_event_list(year: Optional[Year]) -> Response:
    years: List[Year]

    if year is None:
        api_status_sv = ApiStatus.get()
        current_year = api_status_sv["current_season"]
        max_year = api_status_sv["max_season"]
        years = list(range(current_year, max_year + 1))
    else:
        years = [year]

    for year_to_fetch in years:
        taskqueue.add(
            queue_name="datafeed",
            target="py3-tasks-io",
            url=url_for("frc_api.event_list", year=year_to_fetch),
            method="GET",
        )

    template_values = {"year": year, "event_count": year}

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template(
                "datafeeds/usfirst_events_details_enqueue.html", **template_values
            )
        )

    return make_response("")


@blueprint.route("/backend-tasks/get/event_list/<int:year>")
def event_list(year: Year) -> Response:
    df = DatafeedFMSAPI()

    fmsapi_events, event_list_districts = df.get_event_list(year)

    # All regular-season events can be inserted without any work involved.
    # We need to de-duplicate offseason events from the FRC Events API with a different code than the TBA event code
    fmsapi_events_offseason = [e for e in fmsapi_events if e.is_offseason]
    event_keys_to_put = set([e.key_name for e in fmsapi_events]) - set(
        [e.key_name for e in fmsapi_events_offseason]
    )
    events_to_put = [e for e in fmsapi_events if e.key_name in event_keys_to_put]

    (
        matched_offseason_events,
        new_offseason_events,
    ) = OffseasonEventHelper.categorize_offseasons(int(year), fmsapi_events_offseason)

    # For all matched offseason events, make sure the FIRST code matches the TBA FIRST code
    for tba_event, first_event in matched_offseason_events:
        tba_event.first_code = first_event.event_short
        events_to_put.append(tba_event)  # Update TBA events - discard the FIRST event

    # For all new offseason events we can't automatically match, create suggestions
    SuggestionCreator.createDummyOffseasonSuggestions(new_offseason_events)

    events = listify(EventManipulator.createOrUpdate(events_to_put)) or []

    fmsapi_districts = df.get_district_list(year)
    merged_districts = DistrictManipulator.mergeModels(
        fmsapi_districts, event_list_districts
    )
    districts = listify(DistrictManipulator.createOrUpdate(merged_districts))

    # Fetch event details for each event
    for event in events:
        taskqueue.add(
            queue_name="datafeed",
            target="py3-tasks-io",
            url=url_for("frc_api.event_details", event_key=event.key_name),
            method="GET",
        )

    template_values = {
        "events": events,
        "districts": districts,
    }

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template("datafeeds/fms_event_list_get.html", **template_values)
        )

    return make_response("")


@blueprint.route("/backend-tasks/enqueue/event_details/<event_key>")
def enqueue_event_details(event_key: EventKey) -> Response:
    if not Event.validate_key_name(event_key):
        return make_response(f"Bad event key: {escape(event_key)}", 400)

    taskqueue.add(
        queue_name="datafeed",
        target="py3-tasks-io",
        url=url_for("frc_api.event_details", event_key=event_key),
        method="GET",
    )

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            make_response(
                render_template(
                    "datafeeds/fmsapi_eventteams_enqueue.html", event_key=event_key
                )
            )
        )

    return make_response("")


@blueprint.route("/backend-tasks/get/event_details/<event_key>")
def event_details(event_key: EventKey) -> Response:
    if not Event.validate_key_name(event_key):
        return make_response(f"Bad event key: {escape(event_key)}", 400)

    df = DatafeedFMSAPI()

    # Update event
    fmsapi_events, fmsapi_districts = df.get_event_details(event_key)
    new_events = EventManipulator.createOrUpdate(fmsapi_events)
    event = safe_cast(Event, none_throws(new_events))

    DistrictManipulator.createOrUpdate(fmsapi_districts)

    models = df.get_event_teams(event_key)
    teams: List[Team] = []
    district_teams: List[DistrictTeam] = []
    robots: List[Robot] = []
    for group in models:
        # models is a list of tuples (team, districtTeam, robot)
        team = group[0]
        if isinstance(team, Team):
            teams.append(team)

        district_team = group[1]
        if isinstance(district_team, DistrictTeam):
            district_teams.append(district_team)

        robot = group[2]
        if isinstance(robot, Robot):
            robots.append(robot)

    # Write new models
    if (
        teams and event.year == SeasonHelper.get_max_year()
    ):  # Only update from latest year
        teams = TeamManipulator.createOrUpdate(teams)

    district_teams = DistrictTeamManipulator.createOrUpdate(district_teams)
    robots = RobotManipulator.createOrUpdate(robots)

    if not teams:
        # No teams found registered for this event
        teams = []
    if type(teams) is not list:
        teams = [teams]

    # Build EventTeams
    cmp_hack_sitevar = ChampsRegistrationHacks.get()
    events_without_eventteams = cmp_hack_sitevar["skip_eventteams"]
    skip_eventteams = event_key in events_without_eventteams
    event_teams = (
        [
            EventTeam(
                id=event.key_name + "_" + team.key_name,
                event=event.key,
                team=team.key,
                year=event.year,
            )
            for team in teams
        ]
        if not skip_eventteams
        else []
    )

    # Delete eventteams of teams that are no longer registered
    if event_teams and not skip_eventteams:
        existing_event_teams = EventTeam.query(EventTeam.event == event.key).fetch()

        # Don't delete EventTeam models for teams who won Awards at the Event, but who did not attend the Event
        award_teams = set()
        for award in event.awards:
            for team in award.team_list:
                award_teams.add(team.id())
        award_event_teams = {
            et.key for et in existing_event_teams if et.team.id() in award_teams
        }

        event_team_keys = {et.key for et in event_teams}
        existing_event_team_keys = {et.key for et in existing_event_teams}

        et_keys_to_delete = existing_event_team_keys.difference(
            event_team_keys.union(award_event_teams)
        )
        EventTeamManipulator.delete_keys(et_keys_to_delete)

    event_teams = EventTeamManipulator.createOrUpdate(event_teams)
    if type(event_teams) is not list:
        event_teams = [event_teams]

    if event.year >= 2018:
        avatars, keys_to_delete = df.get_event_team_avatars(event.key_name)
        if avatars:
            MediaManipulator.createOrUpdate(avatars)
        MediaManipulator.delete_keys(keys_to_delete)

    template_values = {
        "event": event,
        "event_teams": event_teams,
    }

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template(
                "datafeeds/usfirst_event_details_get.html", **template_values
            )
        )

    return make_response("")


# @blueprint.route("/awards")
# @blueprint.route("/awards/<int:from backend.common.helpers.listify import delistify, listifyyear>")
# TODO: Drop support for this "now" and just use an empty year
@blueprint.route("/tasks/enqueue/fmsapi_awards/now", defaults={"year": None})
@blueprint.route("/tasks/enqueue/fmsapi_awards/<int:year>")
def awards_year(year: Optional[int]) -> Response:
    events: List[Event]
    if year is None:
        events = EventHelper.events_within_a_day()
        events = list(filter(lambda e: e.official, events))
    else:
        event_keys = (
            Event.query(Event.official == True)  # noqa: E712
            .filter(Event.year == year)
            .fetch(keys_only=True)
        )
        events = ndb.get_multi(event_keys)

    for event in events:
        taskqueue.add(
            queue_name="datafeed",
            target="py3-tasks-io",
            url=url_for("frc_api.awards_event", event_key=event.key_name),
            method="GET",
        )

    if (
        "X-Appengine-Taskname" not in request.headers
    ):  # Only write out if not in taskqueue
        return make_response(
            render_template("datafeeds/fmsapi_awards_enqueue.html", events=events)
        )

    return make_response("")


# @blueprint.route("/awards/<event_key>")
@blueprint.route("/tasks/get/fmsapi_awards/<event_key>")
def awards_event(event_key: EventKey) -> Response:
    event = Event.get_by_id(event_key) if Event.validate_key_name(event_key) else None
    if event is None:
        return make_response(f"No Event for key: {escape(event_key)}", 404)

    datafeed = DatafeedFMSAPI()
    awards = datafeed.get_awards(event)

    if event.remap_teams:
        EventRemapTeamsHelper.remapteams_awards(awards, event.remap_teams)

    new_awards = AwardManipulator.createOrUpdate(awards)
    # new_awards could be a single object or None
    new_awards = listify(new_awards)

    # Create EventTeams
    team_ids: Set[TeamKey] = set()
    for award in new_awards:
        for team in award.team_list:
            team_id = none_throws(team.string_id())
            # strip all suffixes (eg B teams)
            team_ids.add("frc" + re.sub("[^0-9]", "", team_id))

    teams = TeamManipulator.createOrUpdate(
        [Team(id=team_id, team_number=int(team_id[3:])) for team_id in team_ids]
    )

    if teams:
        # teams might be a single object
        teams = listify(teams)

        EventTeamManipulator.createOrUpdate(
            [
                EventTeam(
                    id=event_key + "_" + team.key_name,
                    event=event.key,
                    team=team.key,
                    year=event.year,
                )
                for team in teams
            ]
        )

    # Only write out if not in taskqueue
    if "X-Appengine-Taskname" not in request.headers:
        return make_response(
            render_template("datafeeds/fmsapi_awards_get.html", awards=new_awards)
        )

    return make_response("")
