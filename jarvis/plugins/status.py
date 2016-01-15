"""
I am version 1.0.0 of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions.
"""
import contextlib
import logging

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

    def respond(self, ch=None, user=None, msg=None):
        with contextlib.closing(conn.cursor()) as cur:
            admin = cur.execute(""" SELECT is_admin
                                    FROM user
                                    WHERE uuid = ?
                                """, [user]).fetchone()
            if admin and 'power off' in msg:
                self.send(ch, 'As you wish.')
                logger.debug('Shutting down by request.')
                raise KeyboardInterrupt

        if 'you there?' in msg:
            self.send(ch, 'Oh hello, sir!')
        elif 'you up?' in msg:
            self.send(ch, 'At your service, sir.')
        elif 'hello' in msg:
            self.send(ch, 'Hello, I am Jarvis.')
        elif "i'm back" in msg:
            self.send(ch, 'Welcome home, sir...')
        elif 'describe yourself' in msg:
            self.send(ch, __doc__.replace('\n', ' '))
