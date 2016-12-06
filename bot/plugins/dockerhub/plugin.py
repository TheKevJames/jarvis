"""
I am able to understand DockerHub Webhooks and notify the relevant users of
pushes to their followed repositories. Any repository that has a webhook
pointed at `/api/plugin/dockerhub/webhook` can generate notifications.

You can follow your own repositories by telling me your "dockerhub username is
____". You can manage other repositories by telling me to "(un)follow _____ on
dockerhub".
"""
import logging

import aiohttp.web

import jarvis.core.helper as helper
import jarvis.core.plugin as plugin
import jarvis.db.users as users

from .constant import ALREADY_FOLLOWING
from .constant import CREATED_FOLLOW
from .constant import DELETED_FOLLOW
from .constant import IMAGE_PUSHED
from .constant import UPDATED_USERNAME
from .dal import DockerhubDal
from .schema import initialize


logger = logging.getLogger(__name__)


class Dockerhub(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @staticmethod
    def initialize():
        initialize()

    @plugin.Plugin.on_regex(r".*my dockerhub username is (.*)\.?")
    def change_username(self, ch, user, groups):
        DockerhubDal.update_username(user, groups[0])
        self.send(ch, UPDATED_USERNAME(groups[0]))

    @plugin.Plugin.on_regex(r".*unfollow (.*) on dockerhub.*")
    def unfollow_repository(self, ch, user, groups):
        DockerhubDal.delete_follow(user, groups[0])
        self.send(ch, DELETED_FOLLOW(groups[0]))

    @plugin.Plugin.on_regex(r".*follow (.*) on dockerhub.*")
    def follow_repository(self, ch, user, groups):
        if DockerhubDal.create_follow(user, groups[0]):
            self.send(ch, CREATED_FOLLOW(groups[0]))
            return

        self.send(ch, ALREADY_FOLLOWING(groups[0]))

    @plugin.Plugin.on_api('POST', 'webhook')
    async def webhook(self, request):
        json_data = await request.json()

        try:
            repo_name = json_data['repository']['repo_name']
            owner = json_data['repository']['owner']
        except KeyError:
            logger.info('Could not parse webhook data %s.', json_data)
            return aiohttp.web.Response(status=406, text='unparseable webhook')

        uuid = DockerhubDal.read_by_repository(repo_name)
        if uuid:
            channel = users.UsersDal.read(uuid[0])[6]
            ch = helper.get_channel_or_fail(logger, self.slack, channel)
            self.send_now(ch, IMAGE_PUSHED(repo_name))
            return aiohttp.web.Response(text='ok')

        uuid = DockerhubDal.read_by_username(owner)
        if uuid:
            channel = users.UsersDal.read(uuid[0])[6]
            ch = helper.get_channel_or_fail(logger, self.slack, channel)
            self.send_now(ch, IMAGE_PUSHED(repo_name))
            return aiohttp.web.Response(text='ok')

        logger.debug('Received valid but unsupported webhook for %s.',
                     repo_name)
        return aiohttp.web.Response(status=406, text='unsupported repository')
