"""
This module allows you to interact with my status; do stop in and say "hello"!
Admins can also tell me to "shut down" for repairs.
"""
import logging
import sys

import aiohttp.web
import jarvis.core.helper as helper
import jarvis.core.plugin as plugin
import jarvis.db.channels as channels

from .constant import ACQUIESE
from .constant import GREET
from .constant import ONLINE
from .constant import WELCOME_HOME


logger = logging.getLogger(__name__)


class Status(plugin.Plugin):
    def __init__(self, slack):
        super().__init__(slack)

        for channel in channels.ChannelsDal.read(admin_only=True):
            ch = helper.get_channel_or_fail(logger, self.slack, channel)
            self.send_now(ch, ONLINE)

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.require_auth
    @plugin.Plugin.on_words({'shut down'})
    def die(self, ch, _user, _groups):
        self.send_now(ch, ACQUIESE())
        sys.exit(0)

    @plugin.Plugin.on_regex(r".*i'm (back|home).*")
    def home(self, ch, _user, _group):
        self.send(ch, WELCOME_HOME)

    @plugin.Plugin.on_regex(r'.*hello|(you (there|up)).*')
    def you_there(self, ch, _user, _groups):
        self.send(ch, GREET())

    @plugin.Plugin.on_api('GET', 'ping')
    async def ping(self, _request):
        return aiohttp.web.Response(text='ok')
