"""
I am able to understand DockerHub Webhooks and notify the relevant users of
pushes to their followed repositories. Any repository that has a webhook
pointed at `/api/plugin/dockerhub/webhook` can generate notifications.
"""
import logging

import aiohttp.web

import jarvis.core.helper as helper
import jarvis.core.plugin as plugin
import jarvis.db.users as users

from .constant import IMAGE_PUSHED
from .helper import DockerhubHelper


logger = logging.getLogger(__name__)


class Dockerhub(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_api('POST', 'webhook')
    async def webhook(self, request):
        json_data = await request.json()

        try:
            repo_name = json_data['repository']['repo_name']
            owner = json_data['repository']['owner']
        except KeyError:
            logger.info('Could not parse webhook data %s.', json_data)
            return aiohttp.web.Response(status=406, text='unparseable webhook')

        username = DockerhubHelper.username_for_repository(repo_name)
        if username:
            channel = users.UsersDal.read_by_name(username)[6]
            ch = helper.get_channel_or_fail(logger, self.slack, channel)
            self.send_now(ch, IMAGE_PUSHED(repo_name))
            return aiohttp.web.Response(text='ok')

        username = DockerhubHelper.username_for_owner(owner)
        if username:
            channel = users.UsersDal.read_by_name(username)[6]
            ch = helper.get_channel_or_fail(logger, self.slack, channel)
            self.send_now(ch, IMAGE_PUSHED(repo_name))
            return aiohttp.web.Response(text='ok')

        logger.debug('Received valid but unsupported webhook for %s.',
                     repo_name)
        return aiohttp.web.Response(status=406, text='unsupported repository')
