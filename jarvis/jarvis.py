import contextlib
import json
import logging
import time

import slackclient

from .db import conn
from .db import initialize_database
from .error import SlackError
from .plugins import get_plugins


logger = logging.getLogger(__name__)


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

            uuid = user['id']
            first_name = user['profile']['first_name'].lower()
            last_name = user['profile']['last_name'].lower()
            email = user['profile']['email']
            username = user['name']
            is_admin = int(user['is_admin'])
            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(""" INSERT INTO user (uuid, first_name, last_name,
                                                  email, username, is_admin)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, [uuid, first_name, last_name, email, username,
                                  is_admin])
                conn.commit()

        import os.path
        if os.path.exists(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'seed_data.py')):
            from .seed_data import init
            init()

        logger.debug('Done initializing.')

    def input(self, data):
        msg_type = data.get('type')
        if msg_type == 'message':
            msg = data.get('text', '').lower()
            # TODO: consider changing how Jarvis pays attention
            if not msg.startswith('jarvis'):
                return

            channel = data.get('channel')
            ch = self.slack.server.channels.find(channel)
            if not ch:
                logger.error('Could not look up channel %s', channel)
                raise SlackError('Channel {} does not exist.'.format(channel))

            user = data.get('user')
            for plugin in self.plugins:
                plugin.respond(ch=ch, user=user, msg=msg)
            return

        if msg_type == 'user_change':
            user = data.get('user')
            uuid = user['id']
            first_name = user['profile']['first_name'].lower()
            last_name = user['profile']['last_name'].lower()
            email = user['profile']['email']
            username = user['name']
            is_admin = int(user['is_admin'])

            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(""" INSERT OR REPLACE INTO user
                                (uuid, first_name, last_name, email, username,
                                 is_admin)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, [uuid, first_name, last_name, email, username,
                                  is_admin])
                conn.commit()

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
