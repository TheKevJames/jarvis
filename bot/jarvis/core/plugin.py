import asyncio
import collections
import logging
import inspect
import re

import jarvis.core.helper as helper
import jarvis.core.messages as messages
import jarvis.db.channels as channels
import jarvis.db.users as users


logger = logging.getLogger(__name__)


class PluginMetaclass(type):
    @classmethod
    def __prepare__(mcs, _name, _bases, **_kwargs):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, namespace, **_kwargs):
        result = type.__new__(mcs, name, bases, dict(namespace))

        functions = [fn for fn in namespace.values()
                     if isinstance(fn, collections.Callable)]

        result.api_fns = [fn for fn in functions if hasattr(fn, 'route')]
        result.loop_fns = [fn for fn in functions if hasattr(fn, 'looping')]
        result.response_fns = [fn for fn in functions
                               if hasattr(fn, 'regex') or hasattr(fn, 'words')]

        return result


class Plugin(metaclass=PluginMetaclass):
    def __init__(self, slack):
        self.slack = slack
        self.name = self.__class__.__name__.lower()

        self.buffer = None
        self.reset_buffer()

    def reset_buffer(self):
        self.buffer = collections.defaultdict(list)

    @staticmethod
    def check_regex(func, msg):
        try:
            regex_match = func.regex.match(msg)
            return regex_match.groups()
        except AttributeError:
            return False

    @staticmethod
    def check_words(func, msg):
        try:
            if isinstance(func.words, set):
                if not all(word in msg for word in func.words):
                    return False
            else:
                for word in func.words:
                    msg = msg[msg.index(word) + len(word):]
        except (AttributeError, ValueError):
            return False

        return ['ok']

    @staticmethod
    def on_api(method, route):
        def on_api_decorator(func):
            func.method = method
            func.route = '/api/plugin/{}/{}'.format(
                func.__qualname__.split('.')[0].lower(), route)
            return func
        return on_api_decorator

    @staticmethod
    def on_loop(func):
        func.looping = True
        return func

    @staticmethod
    def on_regex(msg):
        def on_regex_decorator(func):
            func.regex = re.compile(msg)
            return func
        return on_regex_decorator

    @staticmethod
    def on_words(msg):
        def on_words_decorator(func):
            func.words = msg
            return func
        return on_words_decorator

    @staticmethod
    def require_auth(func):
        func.auth = True
        return func

    def send(self, channel, message):
        self.buffer[channel].append(message)

    def send_attachment(self, channel, attachment):
        self.slack.api_call(
            'chat.postMessage', channel=channel, as_user=True,
            attachments=[attachment])

    @staticmethod
    def send_now(channel, message):
        channel.send_message(message)

    def upload_now(self, channel, name, filename, filetype):
        self.slack.api_call(
            'files.upload', channels=channel.id, title=name,
            file=open(filename, 'rb'), filename=filename, filetype=filetype)

    def respond(self, ch, user, msg):
        for fn in self.response_fns:
            groups = self.check_words(fn, msg) or self.check_regex(fn, msg)
            if not groups:
                continue

            if hasattr(fn, 'auth') and not users.UsersDal.is_admin(user):
                self.send(ch, messages.NO_AUTHORIZATION)

                for channel in channels.ChannelsDal.read(admin_only=True):
                    c = helper.get_channel_or_fail(logger, self.slack, channel)
                    self.send(c, messages.UNAUTHORIZED_USAGE(user, msg))

                continue

            if inspect.iscoroutinefunction(fn):
                asyncio.ensure_future(fn(self, ch, user, groups))
            else:
                fn(self, ch, user, groups)

            for channel, msgs in self.buffer.items():
                self.send_now(channel, '\n'.join(msgs))
            self.reset_buffer()

            return True

    def help(self, ch):
        raise NotImplementedError

    def initialize(self):
        pass
