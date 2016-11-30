import random


def ACQUIESE():
    return random.choice(('Check.', 'Very good, sir.', 'Yes, sir.'))


def ERROR_NOT_ENABLED():
    return random.choice((
        'Sir, this instance is not weather-ready.',
        'Sorry sir, this instance is not configured for weather.'))


ERROR_RETRIEVING_WEATHER = 'I was unable to retrieve the weather.'
PRINT_WEATHER = """
{}, sir. It's {}. The weather in {} is {} degrees Celsius and {}. Today's
sunrise {} at {} and sunset {} at {}.
""".replace('\n', ' ').format
UPDATED_LOCATION = lambda x: \
    ACQUIESE() + " I've updated your location to {}.".format(x)

WEATHER_URL = ('http://api.worldweatheronline.com/free/v2/weather.ashx?q={}'
               '&format=json&num_of_days=1&includelocation=yes'
               '&showlocaltime=yes&key={}')
