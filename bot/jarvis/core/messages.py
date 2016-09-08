import random


def ACKNOWLEDGE():
    return random.choice((
        'As you wish.', 'Check.', 'For you, sir, always.', 'Very good, sir.',
        'Will do, sir.', 'Yes, sir.'))


def ALL_SETTLED():
    return 'All appears to be settled.'


def ANALYZED_CASH_POOL():
    return "I've analyzed your cash pool."


def CLEANED_UP():
    return random.choice((
        'All wrapped up here, sir. Will there be anything else?',
        "Yes, sir; I've cleaned up the tomfoolery."))


def CONFUSED():
    return "What is it you're trying to achieve, sir?"


def DESCRIBE(version):
    return """
I am version {} of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions. The following modules have been
loaded:
""".format(version).replace('\n', ' ')


def ERROR_ACCESS_URL():
    return 'I could not access that url.'


def ERROR_NOT_ENABLED(action):
    return random.choice((
        'Sir, this instance is not {}-ready.',
        'Sorry sir, this instance is not configured for {}.')).format(action)


def ERROR_RETRIEVING_WEATHER():
    return 'I was unable to retrieve the weather.'


def DEFAULT_CURRENCY(currency):
    return 'My default currency is {}.'.format(currency)


def DISPLAYING(thing):
    return ACKNOWLEDGE() + ' Displaying your {} now:'.format(thing)


def GREET():
    return random.choice((
        'At your service, sir.', 'Hello, I am Jarvis.', 'Oh hello, sir!'))


def NO_AUTHORIZATION():
    return """
You are not authorised to access this area. I am contacting Mr. Stark now.
"""


def NO_CHANNEL_FOUND(channel):
    return 'I could not look up channel "{}".'.format(channel)


def NO_RECORD(thing):
    return 'I have no record of a {}, sir.'.format(thing)


def NO_USAGE():
    return 'It appears no one has used this feature yet.'


def NO_REVERTABLE():
    return 'I could not find a change to revert.'


def ONLINE():
    return 'J.A.R.V.I.S. online.'


def PRINT_WEATHER(greeting, time, loc, temperature, status, sunrise_tense,
                  sunrise, sunset_tense, sunset):
    return """
{}, sir. It's {}. The weather in {} is {} degrees Celsius and {}. Today's
sunrise {} at {} and sunset {} at {}.
""".format(greeting, time, loc, temperature, status, sunrise_tense, sunrise,
           sunset_tense, sunset).replace('\n', ' ')


def SHOW_CASH_POOL_HISTORY_ITEM(source, targets, val, currency, reason):
    return '{} -> {}: ${} {} {}'.format(source, targets, val, currency, reason)


def SHOW_CASH_POOL_ITEM(user, description, value, currency):
    return '{} {} ${} {}'.format(user, description, value, currency)


def SUPPORT(things):
    return 'I support {}.'.format(things)


def UNAUTHORIZED_USAGE(user, msg):
    return 'Unauthorized attempt from {}. Message was: "{}".'.format(user, msg)


def UPDATED_LOCATION(loc):
    return ACKNOWLEDGE() + " I've updated your location to {}.".format(loc)


def WELCOME_HOME():
    return 'Welcome home, sir...'


def WILL_STORE():
    return "I shall store this on the Stark Industries' Central Database."
