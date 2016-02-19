"""
I am version {} of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions. The following modules have been
loaded:
"""
import contextlib
import json
import time

import slackclient

from .api import build_user
from .db import conn
from .db import initialize_database
from .error import SlackError
from .plugins import get_plugins


__version__ = '1.2.3'


class Jarvis(object):
    def __init__(self, token, init=False):
        self.last_ping = 0

        self.slack = slackclient.SlackClient(token)
        self.slack.rtm_connect()

        if init:
            self.init()

        self.plugins = get_plugins(self.slack)

    def init(self):
        initialize_database()

        users = json.loads(self.slack.api_call('users.list'))
        for user in users['members']:
            if user['deleted']:
                continue

            if user['is_bot'] or user['id'] == 'USLACKBOT':
                continue

            user_fields = build_user(self.slack, user)
            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(""" INSERT INTO user
                                (uuid, first_name, last_name, email, username,
                                 is_admin, channel)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, user_fields)
                conn.commit()

    def handle_message(self, channel, text, user):
        with contextlib.closing(conn.cursor()) as cur:
            dm = cur.execute(""" SELECT 1 FROM user WHERE channel = ? """,
                             [channel]).fetchone()

        # TODO: consider changing how Jarvis pays attention to public channels
        if not dm and not text.startswith('jarvis'):
            return

        ch = self.slack.server.channels.find(channel)
        if not ch:
            raise SlackError('Could not look up channel {}.'.format(channel))

        if 'help' in text:
            message = [__doc__.format(__version__).replace('\n', ' ')]
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
        kind = data.get('type')

        channel = data.get('channel')
        text = data.get('text', '').lower()
        user = data.get('user')

        if kind == 'message':
            self.handle_message(channel, text, user)
            return

        # TODO: handle new and changing users differently?
        if kind in ('team_join', 'user_change'):
            user_fields = build_user(self.slack, user)
            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(""" INSERT OR REPLACE INTO user
                                (uuid, first_name, last_name, email, username,
                                 is_admin, channel)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, user_fields)
                conn.commit()
            return

        logger.debug('Did not respond to event %s', data)

    def keepalive(self):
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack.server.ping()
            self.last_ping = now

    def run(self):
        # TODO: interrupt > poll
        while True:
            for message in self.slack.rtm_read():
                self.input(message)

            self.keepalive()
            time.sleep(.1)
