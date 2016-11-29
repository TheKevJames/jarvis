import asyncio
import logging

import slackclient
# https://github.com/slackhq/python-slackclient/issues/118
from websocket import WebSocketConnectionClosedException


logger = logging.getLogger(__name__)


class SlackAsyncRTMReader:
    def __init__(self, slack):
        self.messages = list()
        self.slack = slack

    def __aiter__(self):
        return self

    async def __anext__(self):
        while not self.messages:
            try:
                self.messages = self.slack.rtm_read()
            except WebSocketConnectionClosedException as e:
                logger.error('Caught websocket disconnect, reconnecting...')
                logger.exception(e)

                self.slack.rtm_connect()

            await asyncio.sleep(.1)

        return self.messages.pop(0)


class SlackClient(slackclient.SlackClient):
    def __init__(self, token):
        super().__init__(token)

    async def keepalive(self):
        while True:
            await asyncio.sleep(3)

            try:
                self.server.ping()
            except WebSocketConnectionClosedException as e:
                logger.error('Caught websocket disconnect, reconnecting...')
                logger.exception(e)

                self.rtm_connect()

    def rtm_read(self):
        return SlackAsyncRTMReader(super())


def looping_exception_handler(loop, context):
    loop.stop()
    loop.exception = context.get('exception')
    raise loop.exception
