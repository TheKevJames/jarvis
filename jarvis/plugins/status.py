"""
This module allows you to interact with my status; do stop in and say "hello"!
Admins can also tell me to "shut down" or "reboot" for repairs or upgrades.
"""
import logging
import random
import sys

from jarvis.core.db import get_admin_channels
from jarvis.core.helper import get_channel_or_fail
import jarvis.core.messages as messages
from jarvis.core.plugin import Plugin


logger = logging.getLogger(__name__)


class Status(Plugin):
    def __init__(self, slack):
        super(Status, self).__init__(slack, 'status')

        for channel in get_admin_channels():
            ch = get_channel_or_fail(logger, self.slack, channel)
            self.send_now(ch, messages.ONLINE)

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @Plugin.require_auth
    @Plugin.on_message(r'.*(power|shut) (off|down).*')
    def die(self, ch, _user, _groups):
        self.send_now(ch, messages.ACKNOWLEDGE())
        sys.exit(0)

    @Plugin.on_message(r".*i'm (back|home).*")
    def home(self, ch, _user, _group):
        self.send(ch, messages.WELCOME_HOME)

    @Plugin.on_message(r".*hello|(you (there|up)).*")
    def you_there(self, ch, _user, _groups):
        self.send(ch, messages.GREET())
