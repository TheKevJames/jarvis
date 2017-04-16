import random
import re

import jarvis.core.helper as helper


def ACKNOWLEDGE():
    return random.choice(('Check.', 'Very good, sir.', 'Yes, sir.'))


def CLEANED_UP():
    return random.choice((
        'All wrapped up here, sir. Will there be anything else?',
        "Yes, sir; I've cleaned up the tomfoolery."))


def NO_USAGE():
    return random.choice((
        'I have no record of a cash pool, sir.',
        'It appears no one has used this feature yet.'))


ALL_SETTLED = 'All appears to be settled.'
ANALYZED = "I've analyzed your cash pool."
CONFUSED = "What is it you're trying to achieve, sir?"
DISPLAYING = lambda x: ACKNOWLEDGE() + ' Displaying your {} now:'.format(x)
MALFORMED = 'Sir, take a deep breath. "{}" is not a valid payment form.'.format
NO_REVERTABLE = 'I could not find a change to revert.'
NO_USER = 'User trace incomplete. Could not find "{}".'.format
SHOW_CASH_POOL_HISTORY_ITEM = '{} -> {}: ${} {} {}, added by {} on {}'.format
SHOW_CASH_POOL_ITEM = '{} {} ${} {}'.format

CURRENCIES = ['CAD', 'USD']
CURRENCIES_MSG = 'I support {}.'.format(helper.list_to_language(CURRENCIES[:]))
DEFAULT_CURRENCY = CURRENCIES[0]
DEFAULT_CURRENCY_MSG = 'My default currency is {}.'.format(DEFAULT_CURRENCY)

REGEX_CURRENCY = r'\$([\d\.]+) ?(|{})'.format('|'.join(CURRENCIES).lower())
REGEX_PAID_ONE = re.compile(
    r'(\w+) paid {} for ([ \w]+)'.format(REGEX_CURRENCY))
REGEX_SENT_ONE = re.compile(r'(\w+) sent {} to (\w+)'.format(REGEX_CURRENCY))
