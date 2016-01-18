"""
I am version {} of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions.
"""
import logging
import random
import sys

from .. import __version__
from ..db import get_admin_channels
from ..error import SlackError
from ..plugin import Plugin


logger = logging.getLogger(__name__)


class Status(Plugin):
    def __init__(self, *args, **kwargs):
        super(Status, self).__init__(*args, **kwargs)

        for channel in get_admin_channels():
            ch = self.slack.server.channels.find(channel)
            if not ch:
                logger.error('Could not look up admin channel %s', channel)
                raise SlackError()

            self.send(ch, 'J.A.R.V.I.S. online.')

    @Plugin.on_message(r'.*describe yourself.*')
    def describe(self, ch, _user, _groups):
        self.send(ch, __doc__.format(__version__).replace('\n', ' '))

    @Plugin.require_auth
    @Plugin.on_message(r'.*(power|shut) (off|down).*')
    def die(self, ch, _user, _groups):
        self.send(ch, 'As you wish.')
        logger.debug('Shutting down by request.')
        sys.exit(0)

    @Plugin.on_message(r".*i'm (back|home).*")
    def im_back(self, ch, _user, _groups):
        self.send(ch, 'Welcome home, sir...')

    @Plugin.on_message(r'.*hello|(you (there|up)).*')
    def you_there(self, ch, _user, _groups):
        self.send(ch, random.choice(['At your service, sir.',
                                     'Hello, I am Jarvis.',
                                     'Oh hello, sir!']))