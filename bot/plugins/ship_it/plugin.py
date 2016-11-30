"""
I have been configured to help you "ship it" upon command.
"""
import jarvis.core.plugin as plugin

from .constant import ACQUIESE
from .constant import SQUIRREL


class ShipIt(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_words(['ship', 'it'])
    def ship_it(self, ch, _user, _groups):
        self.send(ch, ACQUIESE())
        self.send(ch, SQUIRREL())
