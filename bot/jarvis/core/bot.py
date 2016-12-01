import asyncio
import functools
import importlib.machinery
import logging
import os
import sys

import aiohttp.web

import jarvis.core.async as async
import jarvis.core.helper as helper
import jarvis.core.messages as messages
import jarvis.db.channels as channels
import jarvis.db.schema as schema
import jarvis.db.users as users


logger = logging.getLogger(__name__)


__version__ = '2.2.1'


class Jarvis:
    def __init__(self, token):
        self.plugins = list()
        self.uuid = None

        try:
            self.slack = async.SlackClient(token)
            self.slack.rtm_connect()

            self.uuid = self.slack.api_call('auth.test')['user_id']
        except Exception as e:
            logger.error('Could not start JARVIS.')
            logger.exception(e)
            sys.exit(1)

    def init(self):
        schema.initialize()

        user_list = self.slack.api_call('users.list')
        for user in user_list['members']:
            if user['deleted']:
                continue

            if user['is_bot'] or user['id'] == 'USLACKBOT':
                continue

            user = helper.get_user_fields(self.slack, user)
            users.UsersDal.create(*user)

            c = helper.get_channel_or_fail(logger, self.slack, user[-1])
            c.send_message(messages.GREET_USER(user))

    def handle_message(self, channel, text, user):
        ch = helper.get_channel_or_fail(logger, self.slack, channel)

        if 'help' in text:
            message = [messages.DESCRIBE(__version__)]
            for plugin in self.plugins:
                message.append('- {}'.format(plugin.name))
                if plugin.name in text:
                    plugin.help(ch=ch)
                    break
            else:
                ch.send_message('\n'.join(message))
            return

        responded = False
        for plugin in self.plugins:
            responded ^= bool(plugin.respond(ch=ch, user=user, msg=text))

        if not responded:
            logger.warning('Could not understand message "%s".', text)
            ch.send_message(messages.CONFUSED)

    def input(self, data):
        try:
            if data.get('username') == 'slackbot':
                return

            user = data.get('user') or data.get('message', {}).get('user')
            if user == self.uuid:
                return

            kind = data.get('type')
            if kind == 'message':
                ch = data.get('channel')
                text = data.get('text', '').lower()

                direct = channels.ChannelsDal.is_direct(ch)
                mention = text.startswith('jarvis')
                if direct or mention:
                    self.handle_message(ch, text, user)
                return

            if kind in ('team_join', 'user_change'):
                if user['is_bot']:
                    return

                user = helper.get_user_fields(self.slack, user)
                users.UsersDal.update(*user)
                return
        except Exception:
            logger.error('Error handling message %s', str(data))
            raise

    async def rtm_respond(self):
        async for message in self.slack.rtm_read():
            self.input(message)
            await asyncio.sleep(0)

    def run(self):
        logger.debug('Configuring event loop...')
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(async.looping_exception_handler)

        asyncio.ensure_future(self.slack.keepalive())
        asyncio.ensure_future(self.rtm_respond())

        app = aiohttp.web.Application()

        logger.debug('Initializing plugins...')
        for name in sorted(os.listdir('/plugins')):
            plugin = importlib.machinery.SourceFileLoader(
                name, '/plugins/{}/__init__.py'.format(name)).load_module()
            plugin = getattr(plugin, plugin.__all__[0])(self.slack)
            self.plugins.append(plugin)

            for function in plugin.api_fns:
                app.router.add_route(function.method, function.route,
                                     functools.partial(function, plugin))

        logger.debug('Building web server...')
        handler = app.make_handler(access_log=None)
        f = loop.create_server(handler, '0.0.0.0', 8080)
        srv = loop.run_until_complete(f)

        try:
            logger.debug('Running')
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            srv.close()
            loop.run_until_complete(srv.wait_closed())
            loop.run_until_complete(app.shutdown())
            loop.run_until_complete(handler.finish_connections(60.0))
            loop.run_until_complete(app.cleanup())
            loop.close()

        if not loop.exception:
            return

        for channel in channels.ChannelsDal.read(admin_only=True):
            c = helper.get_channel_or_fail(logger, self.slack, channel)
            c.send_message(messages.DEATH(loop.exception))

        sys.exit(1)
