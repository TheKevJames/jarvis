#!/usr/bin/env python
from slackclient import SlackClient
import logging
import time

from .error import SlackError
from .plugins import get_plugins


logger = logging.getLogger(__name__)


class Jarvis(object):
    def __init__(self, token):
        self.last_ping = 0

        self.slack = SlackClient(token)
        self.slack.rtm_connect()

        self.plugins = get_plugins(self.slack)

        logger.debug('Done initializing.')

    def input(self, data):
        msg_type = data.get('type')  # Jarvis should only respond to 'message'
        msg = data.get('text', '').lower()
        if msg_type and msg:
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
