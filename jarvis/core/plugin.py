import collections
import logging
import re
import sys

from jarvis.core.db import get_admin_channels
from jarvis.core.db import is_admin
from jarvis.core.helper import get_channel_or_fail
import jarvis.core.messages as messages


logger = logging.getLogger(__name__)


class PluginMetaclass(type):
    @classmethod
    def __prepare__(mcs, _name, _bases, **_kwargs):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, namespace, **_kwargs):
        result = type.__new__(mcs, name, bases, dict(namespace))
        result.response_fns = [fn for fn in namespace.values()
                               if hasattr(fn, 'regex')]
        return result


class Plugin(object):
    __metaclass__ = PluginMetaclass

    def __init__(self, slack, name):
        self.slack = slack
        self.name = name

        self.buffer = None
        self.reset_buffer()

    def reset_buffer(self):
        self.buffer = collections.defaultdict(list)

    @staticmethod
    def on_message(msg):
        def on_message_decorator(func):
            func.regex = re.compile(msg)
            return func
        return on_message_decorator

    @staticmethod
    def require_auth(func):
        func.auth = True
        return func

    def send(self, channel, message):
        self.buffer[channel].append(message)

    @staticmethod
    def send_now(channel, message):
        channel.send_message(message.encode('ascii', 'ignore'))

    def respond(self, ch, user, msg):
        for fn in self.response_fns:
            regex_match = fn.regex.match(msg)
            if not regex_match:
                continue

            if hasattr(fn, 'auth') and not is_admin(user):
                self.send(ch, messages.NO_AUTHORIZATION)

                for channel in get_admin_channels:
                    ch = get_channel_or_fail(logger, self.slack, channel)
                    self.send(ch, UNAUTHORIZED_USAGE.format(user, msg))

                continue

            fn(self, ch, user, regex_match.groups())
            for channel, messages in self.buffer.iteritems():
                self.send_now(channel, '\n'.join(messages))
            self.reset_buffer()

            return

    def help(self, ch):
        raise NotImplementedError
