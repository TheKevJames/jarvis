"""
This module allows you to interact with my status; do stop in and say "hello"!
Admins can also tell me to "shut down" or "reboot" for repairs or upgrades.
"""
import logging
import random
import sys

from jarvis.core.db import get_admin_channels
from jarvis.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Status(Plugin):
    def __init__(self, slack):
        super(Status, self).__init__(slack, 'status')

        for channel in get_admin_channels():
            ch = self.slack.server.channels.find(channel)
            if not ch:
                logger.error(
                    'Could not look up admin channel {}.'.format(channel))
                sys.exit(1)

            self.send_now(ch, 'J.A.R.V.I.S. online.')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @Plugin.require_auth
    @Plugin.on_message(r'.*(power|shut) (off|down).*')
    def die(self, ch, _user, _groups):
        self.send_now(ch, 'As you wish.')
        logger.debug('Shutting down by request.')
        sys.exit(1)

        self.send(ch, 'Remote shutdown unsuccessful.')

    @Plugin.require_auth
    @Plugin.on_message(r'.*reboot yourself.*')
    def reboot(self, ch, _user, _groups):
        self.send_now(ch, 'As you wish.')
        logger.debug('Rebooting by request.')
        sys.exit(0)

        self.send(ch, 'Remote reboot unsuccessful.')

    @Plugin.on_message(r".*i'm (back|home).*")
    def im_back(self, ch, _user, _groups):
        self.send(ch, 'Welcome home, sir...')

    @Plugin.on_message(r'.*hello|(you (there|up)).*')
    def you_there(self, ch, _user, _groups):
        self.send(ch, random.choice(['At your service, sir.',
                                     'Hello, I am Jarvis.',
                                     'Oh hello, sir!']))
