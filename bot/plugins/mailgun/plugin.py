"""
I am able to understand Mailgun Webhooks and inform you of any issues. If you
are a configured user for a domain, you simply need to point your webhooks for
that domain to `/api/plugin/mailgun/webhook` to begin receiving event
notifications.

You can follow a mail server by telling me "your mail server is _____". If you
switch to a new server, simply tell my you "don't use _____ as a mail server".
"""
import logging

import aiohttp.web

import jarvis.core.helper as helper
import jarvis.core.plugin as plugin
import jarvis.db.users as users

from .constant import ALREADY_FOLLOWING
from .constant import BOUNCED
from .constant import COMPLAINED
from .constant import CREATED_FOLLOW
from .constant import DELETED_FOLLOW
from .constant import DROPPED
from .dal import MailgunDal
from .helper import MailgunHelper
from .schema import initialize


logger = logging.getLogger(__name__)


class Mailgun(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @staticmethod
    def initialize():
        initialize()

    @plugin.Plugin.on_regex(r'.*my mail ?server is <.*\|(.*)>\.?')
    def follow_domain(self, ch, user, groups):
        if MailgunDal.create_domain(user, groups[0]):
            self.send(ch, CREATED_FOLLOW(groups[0]))
            return

        self.send(ch, ALREADY_FOLLOWING(groups[0]))

    @plugin.Plugin.on_regex(r".*i don't use <.*\|(.*)> as a mail ?server.*")
    def unfollow_domain(self, ch, user, groups):
        MailgunDal.delete_domain(user, groups[0])
        self.send(ch, DELETED_FOLLOW(groups[0]))

    @plugin.Plugin.on_api('POST', 'webhook')
    async def webhook(self, request):
        post_data = await request.post()

        response = MailgunHelper.validate(post_data['signature'],
                                          post_data['timestamp'],
                                          post_data['token'])
        if response:
            return response

        domain = post_data['domain']
        uuid = MailgunDal.read_by_domain(domain)
        if not uuid:
            logger.info('Could not look up user for domain %s.', domain)
            return aiohttp.web.Response(status=406, text='unsupported domain')

        channel = users.UsersDal.read(uuid[0])[6]
        ch = helper.get_channel_or_fail(logger, self.slack, channel)

        event = post_data['event']
        # if event == 'clicked':
        #     pass
        if event == 'bounced':
            self.send_now(ch, BOUNCED(domain, post_data['recipient'],
                                      post_data['error']))
            return aiohttp.web.Response(text='ok')
        elif event == 'complained':
            self.send_now(ch, COMPLAINED(domain, post_data['recipient']))
            return aiohttp.web.Response(text='ok')
        elif event == 'delivered':
            return aiohttp.web.Response(text='ok')
        elif event == 'dropped':
            self.send_now(ch, DROPPED(domain, post_data['recipient'],
                                      post_data['description'].lower()))
            return aiohttp.web.Response(text='ok')
        # elif event == 'opened':
        #     pass
        # elif event == 'unsubscribed':
        #     pass

        logger.warning('Received valid but unsupported webhook (%s).', event)
        return aiohttp.web.Response(status=406, text='unsupported event')
