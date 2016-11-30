import hashlib
import hmac
import logging
import os
import time

import aiohttp.web

from .config import DOMAINS


MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')


logger = logging.getLogger(__name__)


class MailgunHelper:
    tokens = set()

    @staticmethod
    def username_for_domain(domain):
        return DOMAINS.get(domain)

    @classmethod
    def validate(cls, signature, timestamp, token):
        # Ensure request is not out-of-date
        now = time.time()
        if now - timestamp > 60:
            logger.info('Rejected stale webhook with timestamp %s at %s.',
                        timestamp, now)
            return aiohttp.web.Response(status=422, text='stale data')

        # Ensure request is not a replay
        if token in cls.tokens:
            logger.info('Rejected replayed webhook with token %s.', token)
            return aiohttp.web.Response(status=409, text='invalid token')

        cls.tokens.add(token)

        # Ensure request is authenticated
        key = MAILGUN_API_KEY
        if not key:
            return aiohttp.web.Response(status=500, text='missing API key')

        hexdigest = hmac.new(key=key.encode(),
                             msg='{}{}'.format(timestamp, token).encode(),
                             digestmod=hashlib.sha256).hexdigest()
        if hexdigest != signature:
            logger.info('Rejected webhook with bad digest.')
            return aiohttp.web.Response(status=403, text='invalid signature')
