import collections
import re

from .db import is_admin


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

    def __init__(self, slack):
        self.slack = slack

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
                continue

            fn(self, ch, user, regex_match.groups())
            return
