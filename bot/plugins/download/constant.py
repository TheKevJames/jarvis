import os
import random


def ACQUIESE():
    return random.choice(('As you wish.', 'Check.', 'For you, sir, always.',
                          'Yes, sir.'))


def ERROR_NOT_ENABLED():
    return random.choice((
        'Sir, this instance is not torrent-ready.',
        'Sorry sir, this instance is not configured for torrenting.'))


ERROR_ACCESSING_URL = 'I could not access that URL.'
WILL_STORE = "I shall store this on the Stark Industries' Central Database."

COMPLETED_DIR = os.path.join(os.path.abspath(os.sep), 'torrent', 'done')
ONGOING_DIR = os.path.join(os.path.abspath(os.sep), 'torrent', 'incomplete')
WATCH_DIR = os.path.join(os.path.abspath(os.sep), 'torrent', 'watch')
