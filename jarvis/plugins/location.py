"""
You can ask me "how's the weather" if you would like an overview of the weather
in your location. Do I have the wrong location? Please inform me of my
inadequacies by telling me "I'm in _________."
"""
import contextlib
import logging
import os
import re
import requests

from ..db import conn
from ..plugin import Plugin


logger = logging.getLogger(__name__)


MOVED = re.compile(r"jarvis.* i'm in ([ \w]+)")
WEATHER_URL = ('http://api.worldweatheronline.com/free/v2/weather.ashx?q=%s'
               '&format=json&num_of_days=1&includelocation=yes'
               '&showlocaltime=yes&key=%s')


class Location(Plugin):
    def __init__(self, slack):
        super(Location, self).__init__(slack, 'location')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    def respond(self, ch=None, user=None, msg=None):
        # TODO: consider moving this to a user-management plugin
        if "i'm in" in msg:
            place = msg[msg.find("i'm in") + 7:].strip('.')

            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(""" INSERT OR REPLACE INTO user_data (uuid, place)
                                VALUES (?, ?)""", [user, place])
                conn.commit()

            self.send(
                ch, "Very good, sir. I've updated your location to {}.".format(
                    place))
            return

        if "how's the weather" in msg:
            with contextlib.closing(conn.cursor()) as cur:
                place = cur.execute(""" SELECT place
                                        FROM user_data
                                        WHERE uuid = ?
                                    """, [user]).fetchone() or 'Waterloo'

            try:
                token = os.environ['WORLD_WEATHER_TOKEN']
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

                hour = int(time.split(':')[0])
                if 5 <= hour < 12:
                    greeting = 'Good morning'
                elif 12 <= hour < 17:
                    greeting = 'Good afternoon'
                elif 17 <= hour < 23:
                    greeting = 'Good evening'
                else:
                    greeting = "You're up late"

                # TODO: past/future tense
                self.send(
                    ch, "{}, sir. It's {}. The weather in {} is {} degrees "
                        "Celsius and {}. Today's sunrise and sunset occur "
                        "at {} and {}".format(
                            greeting, time, city, current['temp_C'],
                            description, sunrise, sunset))
            except Exception as e:
                logger.error('Error retrieving weather.')
                logger.exception(e)
                self.send(ch, 'I was unable to retrieve the weather.')

            return
