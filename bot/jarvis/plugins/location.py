"""
You can ask me "how's the weather" if you would like an overview of the weather
in your location. Do I have the wrong location? Please inform me of my
inadequacies by telling me "I'm in _________."
"""
import logging
import os
import requests

import jarvis.core.helper as helper
import jarvis.core.messages as messages
import jarvis.core.plugin as plugin
import jarvis.db.dal as dal


logger = logging.getLogger(__name__)


WEATHER_URL = ('http://api.worldweatheronline.com/free/v2/weather.ashx?q=%s'
               '&format=json&num_of_days=1&includelocation=yes'
               '&showlocaltime=yes&key=%s')


class LocationDal(dal.Dal):
    # pylint: disable=E0213
    default_location = 'waterloo'

    def read(cur, uuid):
        loc = cur.execute(""" SELECT place FROM user_data WHERE uuid = ? """,
                          [uuid]).fetchone()
        return loc[0] if loc else LocationDal.default_location

    def update(cur, uuid, place):
        cur.execute(""" INSERT OR REPLACE INTO user_data (uuid, place)
                        VALUES (?, ?)""", [uuid, place])


class Location(plugin.Plugin):
    def __init__(self, slack):
        super(Location, self).__init__(slack, 'location')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_regex(r".*i'm in (.*)\.?")
    def change_location(self, ch, user, groups):
        LocationDal.update(user, groups[0])
        self.send(ch, messages.UPDATED_LOCATION(groups[0]))

    @plugin.Plugin.on_words({'weather'})
    def get_weather(self, ch, user, _groups):
        token = os.environ.get('WORLD_WEATHER_TOKEN')
        if not token:
            self.send(ch, messages.ERROR_NOT_ENABLED('weather'))
            return

        place = LocationDal.read(user)

        rsp = requests.get(WEATHER_URL % (place, token)).json()['data']
        if 'error' in rsp:
            raise Exception(rsp)

        # API parsing
        astronomy = rsp['weather'][0]['astronomy'][0]
        city = rsp['nearest_area'][0]['areaName'][0]['value']
        current = rsp['current_condition'][0]
        description = current['weatherDesc'][0]['value'].lower()
        time = rsp['time_zone'][0]['localtime'].split(' ')[1]
        sunrise = astronomy['sunrise'].lstrip('0')
        sunset = astronomy['sunset'].lstrip('0')

        hour, minutes = map(int, time.split(':'))
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

        self.send(ch, messages.PRINT_WEATHER(
            greeting, time, city, current['temp_C'], description,
            sunrise_tense, sunrise, sunset_tense, sunset))
