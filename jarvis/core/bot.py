import contextlib
import logging
import sys
import time

import slackclient

from jarvis.core.db import create_user
from jarvis.core.db import update_user
from jarvis.core.db import initialize_database
from jarvis.core.db import is_direct_channel
from jarvis.core.helper import get_channel_or_fail
from jarvis.core.messages import DESCRIBE
from jarvis.core.messages import UPDATED
from jarvis.plugins import get_plugins


logger = logging.getLogger(__name__)


try:
    from setuptools_scm import get_version
    __version__ = get_version()
except Exception as e:
    logger.error('Could not get version information.')
    logger.exception(e)
    __version__ = 'xxx-version-error'


IGNORED_EVENTS = {
    'channel_joined',
    'dnd_updated_user',
    'file_shared',
    'hello',
    'pong',
    'pin_added',
    'pin_removed',
    'presence_change',
    'reaction_added',
    'reaction_removed',
    'reconnect_url',
    'user_typing',
}


# MonkeyPatch for slackclient not properly supporting Python 3
slackclient._channel.Channel.__hash__ = lambda self: hash(self.id)


class Jarvis(object):
    def __init__(self, token, init=False):
        self.last_ping = 0
        self.plugins = None

        try:
            self.slack = slackclient.SlackClient(token)
            self.slack.rtm_connect()
        except Exception as e:
            logger.error('Could not start JARVIS.')
            logger.exception(e)
            sys.exit(1)

    def init(self):
        initialize_database()

        users = self.slack.api_call('users.list')
        for user in users['members']:
            if user['deleted']:
                continue

            if user['is_bot'] or user['id'] == 'USLACKBOT':
                continue

            create_user(self.slack, user)

    def update(self):
        ch = get_channel_or_fail(logger, self.slack, 'general')
        ch.send_message(UPDATED.format(__version__))

    def handle_message(self, channel, text, user):
        ch = get_channel_or_fail(logger, self.slack, channel)

        if 'help' in text:
            message = [DESCRIBE.format(__version__)]
            for plugin in self.plugins:
                message.append('- {}'.format(plugin.name))
                if plugin.name in text:
                    plugin.help(ch=ch)
                    break
            else:
                ch.send_message('\n'.join(message))
            return

        for plugin in self.plugins:
            plugin.respond(ch=ch, user=user, msg=text)

    def input(self, data):
        kind = data.get('type', 'pong')
        if kind in IGNORED_EVENTS:
            return

        channel = data.get('channel')
        text = data.get('text', '').lower()
        user = data.get('user')

        if kind == 'message':
            if is_direct_channel(channel) or text.startswith('jarvis'):
                self.handle_message(channel, text, user)
        elif kind in ('team_join', 'user_change'):
            update_user(self.slack, user)
        else:
            logger.debug('Did not respond to event %s', data)

    def keepalive(self):
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack.server.ping()
            self.last_ping = now

    def run(self):
        try:
            self.plugins = get_plugins(self.slack)

            while True:
                for message in self.slack.rtm_read():
                    self.input(message)

                self.keepalive()
                time.sleep(.1)
        except Exception as e:
            logger.exception(e)
            sys.exit(1)
