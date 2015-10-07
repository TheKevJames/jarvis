import logging
import requests
from datetime import datetime
from pytz import timezone


# TODO: get user location
LOCATION = 'Waterloo,Ontario'
URL = 'http://api.openweathermap.org/data/2.5/weather?q='


crontable = []
outputs = []


logger = logging.getLogger(__name__)


def process_message(data):
    if "how's the weather?" in data['text']:
        info = []

        try:
            response = requests.get(URL + LOCATION).json()

            tz = timezone('US/Eastern')
            time = datetime.now(tz)

            hr = time.hour
            if 5 <= hr < 12:
                info.append('Good morning, sir.')
            elif 12 <= hr < 17:
                info.append('Good afternoon, sir.')
            elif 17 <= hr < 23:
                info.append('Good evening, sir.')
            else:
                info.append("You're up late, sir.")

            hour = hr if 0 < hr <= 12 else abs(hr - 12)
            minute = str(time.minute).rjust(2, '0')
            part = 'a.m.' if hr < 12 else 'p.m.'
            info.append("It's %s:%s %s" % (hour, minute, part))

            description = response['weather'][0]['description']
            if description == 'sky is clear':
                description = 'a clear sky'

            info.append('The weather in %s is %g degrees Celcius with %s.' %
                        (response['name'], response['main']['temp'] - 273.15,
                         description))

            info.append("Today's forecast ranges between %g and %g degrees." %
                        (response['main']['temp_min'] - 273.15,
                         response['main']['temp_max'] - 273.15))

            outputs.append([data['channel'], ' '.join(info)])
        except Exception as e:
            logger.error('Error retrieving weather.')
            logger.exception(e)
            outputs.append([data['channel'],
                            'I was unable to retrieve the weather.'])
