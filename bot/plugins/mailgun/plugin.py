"""
I am able to understand Mailgun Webhooks and inform you of any issues. If you
are a configured user for a domain, you simply need to point your webhooks for
that domain to `/api/plugin/mailgun/webhook` to begin receiving event
notifications.
"""
import logging

import aiohttp.web

import jarvis.core.helper as helper
import jarvis.core.plugin as plugin
import jarvis.db.users as users

from .constant import BOUNCED
from .constant import COMPLAINED
from .constant import DROPPED
from .helper import MailgunHelper


logger = logging.getLogger(__name__)


class Mailgun(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_api('POST', 'webhook')
    async def webhook(self, request):
        post_data = await request.post()

        response = MailgunHelper.validate(post_data['signature'],
                                          float(post_data['timestamp']),
                                          post_data['token'])
        if response:
            return response

        domain = post_data['domain']
        username = MailgunHelper.username_for_domain(domain)
        if not username:
            logger.info('Could not look up user for domain %s.', domain)
            return aiohttp.web.Response(status=406, text='unsupported domain')

        channel = users.UsersDal.read_by_name(username)[6]
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
        # elif event == 'delivered':
        #     pass
        elif event == 'dropped':
            self.send_now(ch, DROPPED(domain, post_data['recipient'],
                                      post_data['description'].lower()))
            return aiohttp.web.Response(text='ok')
        # elif event == 'opened':
        #     pass
        # elif event == 'unsubscribed':
        #     pass

        logger.debug('Received valid but unsupported webhook (%s).', event)
        return aiohttp.web.Response(status=406, text='unsupported event')
