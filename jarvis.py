#!/usr/bin/env python
from slackclient import SlackClient
import glob
import logging
import os
import sys
import time


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    filename='jarvis.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s')

log = logging.getLogger('requests')
log.setLevel(logging.WARNING)


class Jarvis(object):
    def __init__(self, directory, token):
        self.last_ping = 0

        self.slack_client = SlackClient(token)
        self.slack_client.rtm_connect()

        for plugin in glob.glob(directory + '/plugins/*'):
            sys.path.insert(0, plugin)
            sys.path.insert(0, directory + '/plugins/')

        self.plugins = []
        for plugin in glob.glob(directory + '/plugins/*.py') + \
                glob.glob(directory + '/plugins/*/*.py'):
            name = plugin.split('/')[-1][:-3]
            self.plugins.append(Plugin(name))

        logger.debug('Done initializing.')

    def input(self, data):
        if 'type' in data and 'text' in data:
            data['text'] = data['text'].lower()
            if not data['text'].startswith('jarvis'):
                return

            function_name = 'process_' + data['type']
            for plugin in self.plugins:
                plugin.input(function_name, data)

    def keepalive(self):
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def output(self):
        for plugin in self.plugins:
            for output in plugin.output():
                channel = self.slack_client.server.channels.find(output[0])
                if channel and output[1]:
                    message = output[1].encode('ascii', 'ignore')
                    channel.send_message('{}'.format(message))

    def run(self):
        while True:
            for reply in self.slack_client.rtm_read():
                self.input(reply)

            self.output()

            self.keepalive()
            time.sleep(.1)


class Plugin(object):
    def __init__(self, name):
        self.module = __import__(name)

    def input(self, function_name, data):
        if function_name in dir(self.module):
            getattr(self.module, function_name)(data)

    def output(self):
        output = self.module.outputs[:]
        self.module.outputs = []

        return output


def run():
    try:
        directory = os.path.dirname(os.path.realpath(__name__))
        token = os.environ['SLACK_TOKEN']

        jarvis = Jarvis(directory, token)
    except Exception as e:
        logger.error('Error initializing JARVIS.')
        logger.exception(e)
        sys.exit(-1)

    try:
        jarvis.run()
    except KeyboardInterrupt:
        logger.info('Caught KeyboardInterrupt, shutting down.')
        ch = jarvis.slack_client.server.channels.find('D0ATCUTN1')
        if ch:
            msg = 'I actually think I need to sleep now, sir.'.encode('ascii',
                                                                      'ignore')
            ch.send_message('{}'.format(msg))

        sys.exit(0)
    except Exception as e:
        logger.error('Error running JARVIS.')
        logger.exception(e)

        ch = jarvis.slack_client.server.channels.find('D0ATCUTN1')
        if ch:
            msg = 'I think I may be malfunctioning, sir.'.encode('ascii',
                                                                 'ignore')
            ch.send_message('{}'.format(msg))

        sys.exit(-1)


if __name__ == '__main__':
    run()
