import collections
import logging
import re

from .db import get_admin_channels
from .db import is_admin
from .error import SlackError


logger = logging.getLogger(__name__)


class PluginMetaclass(type):
    @classmethod
    def __prepare__(mcs, _name, _bases, **_kwargs):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, namespace, **_kwargs):
        result = type.__new__(mcs, name, bases, dict(namespace))
        result.response_fns = [fn for fn in sorted(namespace.values())
                               if hasattr(fn, 'regex')]
        return result


class Plugin(object):
    __metaclass__ = PluginMetaclass

    def __init__(self, slack, name):
        self.slack = slack
        self.name = name

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

    # TODO: buffer, send in one message. Maybe a self.send_buffered?
    @staticmethod
    def send(channel, message):
        channel.send_message(message.encode('ascii', 'ignore'))

    def respond(self, ch, user, msg):
        for fn in self.response_fns:
            regex_match = fn.regex.match(msg)
            if not regex_match:
                continue

            if hasattr(fn, 'auth') and not is_admin(user):
                self.send(ch, 'You are not authorised to access this area. '
                              'I am contacting Mr. Stark now.')

                for channel in get_admin_channels:
                    ch = self.slack.server.channels.find(channel)
                    if not ch:
                        logger.error('Could not look up channel %s', channel)
                        raise SlackError(
                            'Channel {} does not exist.'.format(channel))

                    self.send(ch, 'Unauthorized attempt from {}. '
                                  'Message was: {}'.format(user, msg))

                continue

            fn(self, ch, user, regex_match.groups())
            return

    def help(self, ch):
        raise NotImplementedError
