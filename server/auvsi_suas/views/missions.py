"""Missions view."""

import json
import logging
from auvsi_suas.models import MissionConfig
from auvsi_suas.views import logger
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError


def active_mission():
    """Gets the single active mission.

    Returns:
        (MissionConfig, HttpResponse). The MissionConfig is the single active
        mission, or None if there is an error. HttpResponse is None if a config
        could be obtained, or the error message if not.
    """
    missions = MissionConfig.objects.filter(is_active=True)
    if len(missions) != 1:
        logging.warning('Invalid number of active missions. Missions: %s.',
                        str(missions))
        return (None,
                HttpResponseServerError('Invalid number of active missions.'))
    return (missions[0], None)


def mission_for_request(request_params):
    """Gets the mission for the request.

    Args:
        request_params: The request parameter dict. If this has a 'mission'
            parameter, it will get the corresponding mission.
    Returns:
        Returns (MissionConfig, HttpResponse). The MissionConfig is
        the one corresponding to the request parameter, or the single active
        MissionConfig if one exists. The HttpResponse is the appropriate error
        if a MissionConfig could not be obtained.
    """
    # If specific mission requested, get it.
    if 'mission' in request_params:
        try:
            mission_id_str = request_params['mission']
            mission_id = int(mission_id_str)
            mission = MissionConfig.objects.get(pk=mission_id)
            return (mission, None)
        except ValueError:
            logging.warning('Invalid mission ID given. ID: %d.', mission_id_str)
            return (None,
                    HttpResponseBadRequest('Mission ID is not an integer.'))
        except MissionConfig.DoesNotExist:
            logging.warning('Given mission ID not found. ID: %d.', mission_id)
            return (None, HttpResponseBadRequest('Mission not found.'))

    # Mission not specified, get the single active mission.
    return active_mission()


# Require admin access
@user_passes_test(lambda u: u.is_superuser)
def missions(request):
    """Gets a list of all missions."""
    # Only GET requests
    if request.method != 'GET':
        logger.warning('Invalid request method for missions request.')
        logger.debug(request)
        return HttpResponseBadRequest('Request must be GET request.')

    missions = MissionConfig.objects.all()
    out = []

    for mission in missions:
        out.append(mission.json())

    return HttpResponse(json.dumps(out), content_type="application/json")