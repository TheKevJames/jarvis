"""
You can ask me "how's the weather" if you would like an overview of the weather
in your location. Do I have the wrong location? Please inform me of my
inadequacies by telling me "I'm in _________."
"""
import logging
import os
import requests

import jarvis.core.helper as helper
import jarvis.core.plugin as plugin

from .constant import ERROR_NOT_ENABLED
from .constant import ERROR_RETRIEVING_WEATHER
from .constant import PRINT_WEATHER
from .constant import UPDATED_LOCATION
from .constant import WEATHER_URL
from .dal import LocationDal
from .schema import initialize


logger = logging.getLogger(__name__)


class Location(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @staticmethod
    def initialize():
        initialize()

    @plugin.Plugin.on_regex(r".*i'm in (.*)\.?")
    def change_location(self, ch, user, groups):
        LocationDal.update(user, groups[0])
        self.send(ch, UPDATED_LOCATION(groups[0]))

    @plugin.Plugin.on_words({'weather'})
    def get_weather(self, ch, user, _groups):  # pylint: disable=too-many-locals
        token = os.environ.get('WORLD_WEATHER_TOKEN')
        if not token:
            self.send(ch, ERROR_NOT_ENABLED())
            return

        place = LocationDal.read(user)

        rsp = requests.get(WEATHER_URL.format(place, token)).json()['data']
        if rsp.get('error'):
            logger.error(rsp.get('error'))
            self.send(ch, ERROR_RETRIEVING_WEATHER)
            return

        # API parsing
        astronomy = rsp['weather'][0]['astronomy'][0]
        city = rsp['nearest_area'][0]['areaName'][0]['value']
        current = rsp['current_condition'][0]
        description = current['weatherDesc'][0]['value'].lower()
        time = rsp['time_zone'][0]['localtime'].split(' ')[1]
        sunrise = astronomy['sunrise'].lstrip('0')
        sunset = astronomy['sunset'].lstrip('0')

        hour, minutes = time.split(':')
        hour, minutes = int(hour), int(minutes)
        if 5 <= hour < 12:
            greeting = 'Good morning'
        elif 12 <= hour < 17:
            greeting = 'Good afternoon'
        elif 17 <= hour < 23:
            greeting = 'Good evening'
        else:
            greeting = "You're up late"

        sunrise_tense = 'is'
        rise_hrs, rise_mins = helper.human_time_to_actual(sunrise)
        if hour > rise_hrs or (hour == rise_hrs and minutes == rise_mins):
            sunrise_tense = 'was'

        sunset_tense = 'will be'
        set_hrs, set_mins = helper.human_time_to_actual(sunset)
        if hour > set_hrs or (hour == set_hrs and minutes == set_mins):
            sunset_tense = 'was'

        # pylint: disable=too-many-format-args
        self.send(ch, PRINT_WEATHER(
            greeting, time, city, current['temp_C'], description,
            sunrise_tense, sunrise, sunset_tense, sunset))
