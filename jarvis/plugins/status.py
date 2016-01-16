"""
I am version 1.1.0 of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions.
"""
import contextlib
import logging
import random
import sys

from ..db import conn
from ..error import SlackError
from ..plugin import Plugin


logger = logging.getLogger(__name__)


class Status(Plugin):
    def __init__(self, *args, **kwargs):
        super(Status, self).__init__(*args, **kwargs)

        with contextlib.closing(conn.cursor()) as cur:
            for user in cur.execute(""" SELECT channel
                                        FROM user
                                        WHERE is_admin = 1
                                    """).fetchall():
                ch = self.slack.server.channels.find(user[0])
                if not ch:
                    logger.error('Could not look up admin channel %s', user[0])
                    raise SlackError()

                self.send(ch, 'J.A.R.V.I.S. online.')

    @Plugin.on_message(r'.*describe yourself.*')
    def describe(self, ch, _user, _groups):
        self.send(ch, __doc__.replace('\n', ' '))

    @Plugin.on_message(r'.*(power off|shut down).*')
    def die(self, ch, user, _groups):
        with contextlib.closing(conn.cursor()) as cur:
            admin = cur.execute(""" SELECT is_admin
                                    FROM user
                                    WHERE uuid = ?
                                """, [user]).fetchone()[0]

        if admin:
            self.send(ch, 'As you wish.')
            logger.debug('Shutting down by request.')
            sys.exit(0)

    @Plugin.on_message(r".*i'm (back|home).*")
    def im_back(self, ch, _user, _groups):
        self.send(ch, 'Welcome home, sir...')

    @Plugin.on_message(r'.*hello|(you (there|up)).*')
    def you_there(self, ch, _user, _groups):
        self.send(ch, random.choice(['At your service, sir.',
                                     'Hello, I am Jarvis.',
                                     'Oh hello, sir!']))
