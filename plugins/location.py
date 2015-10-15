import cPickle as pickle
import logging
import os
import re
import requests


outputs = []


MOVED = re.compile(r"jarvis.* i'm in ([ \w]+)")
WEATHER_URL = ('http://api.worldweatheronline.com/free/v2/weather.ashx?q=%s'
               '&format=json&num_of_days=1&includelocation=yes'
               '&showlocaltime=yes&key=%s')


logger = logging.getLogger(__name__)


LOCATION_FILE = 'location.pickle'
try:
    locations = pickle.load(open(LOCATION_FILE, 'rb'))
except IOError:
    locations = dict()


def process_message(data):
    moved = MOVED.match(data['text'])
    if moved:
        place = moved.groups()

        locations[data['user']] = place
        pickle.dump(locations, open(LOCATION_FILE, 'wb'))

        outputs.append(
            [data['channel'],
             "Very good, sir. I've updated your location to %s." % place])
        return

    if "how's the weather?" in data['text']:
        info = []

        try:
            place = 'Waterloo'
            if data['user'] in locations:
                place = locations[data['user']]

            token = os.environ['WORLD_WEATHER_TOKEN']
            response = requests.get(WEATHER_URL % (place, token)).json()

            if 'error' in response['data']:
                outputs.append(
                    [data['channel'],
                     'I was unable to retrieve the weather for %s.' % place])
                return

            # API parsing
            astronomy = response['data']['weather'][0]['astronomy'][0]
            city = response['data']['nearest_area'][0]['areaName'][0]['value']
            current = response['data']['current_condition'][0]
            description = current['weatherDesc'][0]['value'].lower()
            time = response['data']['time_zone'][0]['localtime'].split(' ')[1]
            sunrise = astronomy['sunrise'].lstrip('0')
            sunset = astronomy['sunset'].lstrip('0')

            hour = int(time.split(':')[0])
            if 5 <= hour < 12:
                info.append('Good morning, sir.')
            elif 12 <= hour < 17:
                info.append('Good afternoon, sir.')
            elif 17 <= hour < 23:
                info.append('Good evening, sir.')
            else:
                info.append("You're up late, sir.")

            info.append("It's %s." % time)

            info.append('The weather in %s is %s degrees Celsius and %s.' %
                        (city, current['temp_C'], description))

            # TODO: past/future tense
            info.append("Today's sunrise and sunset occur at %s and %s." %
                        (sunrise, sunset))

            outputs.append([data['channel'], ' '.join(info)])
            return
        except Exception as e:
            logger.error('Error retrieving weather.')
            logger.exception(e)
            outputs.append([data['channel'],
                            'I was unable to retrieve the weather.'])
            return
