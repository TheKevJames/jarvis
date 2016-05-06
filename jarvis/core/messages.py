# pylint: disable=E302
import random


def ACKNOWLEDGE():
    return random.choice((
        'As you wish.', 'Check.', 'For you, sir, always.', 'Very good, sir.',
        'Will do, sir.', 'Yes, sir.'))
CONFUSED = "What is it you're trying to achieve, sir?"
def GREET():
    return random.choice((
        'At your service, sir.', 'Hello, I am Jarvis.', 'Oh hello, sir!'))
ONLINE = 'J.A.R.V.I.S. online.'
WELCOME_HOME = 'Welcome home, sir...'


DESCRIBE = """
I am version {} of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions. The following modules have been
loaded:
""".replace('\n', ' ')
UPDATED = """
I have been updated. I am now version {} of the J.A.R.V.I.S. natural language
interface for Slack.
""".replace('\n', ' ')


def CLEANED_UP():
    return random.choice((
        'All wrapped up here, sir. Will there be anything else?',
        "Yes, sir; I've cleaned up the tomfoolery."))
ERROR_ACCESS_URL = 'I could not access that url.'
def ERROR_NOT_ENABLED():
    return random.choice((
        'Sir, this instance is not {}-ready.',
        'Sorry sir, this instance is not configured for {}.'))
ERROR_RETRIEVING_WEATHER = 'I was unable to retrieve the weather.'
DEFAULT_CURRENCY = 'My default currency is {}.'
def DISPLAYING():
    return ACKNOWLEDGE() + ' Displaying your {} now:'
NO_AUTHORIZATION = """
You are not authorised to access this area. I am contacting Mr. Stark now.
"""
NO_CHANNEL_FOUND = 'I could not look up channel "{}".'
NO_RECORD = 'I have no record of a {}, sir.'
NO_USAGE = 'It appears no one has used this feature yet.'
NO_REVERTABLE = 'I could not find a change to revert.'
PRINT_WEATHER = """
{}, sir. It's {}. The weather in {} is {} degrees Celsius and {}. Today's
sunrise and sunset occur at {} and {}.
""".replace('\n', ' ')
SUPPORT = 'I support {}.'
UNAUTHORIZED_USAGE = 'Unauthorized attempt from {}. Message was: "{}".'
def UPDATED_LOCATION():
    return ACKNOWLEDGE() + " I've updated your location to {}."
WILL_STORE = "I shall store this on the Stark Industries' Central Database."
