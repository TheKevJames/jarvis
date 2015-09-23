#!/usr/bin/env python
from slackclient import SlackClient
import glob
import os
import sys
import time


DAEMON = False


class Jarvis(object):
    def __init__(self, token):
        self.last_ping = 0

        self.slack_client = SlackClient(token)
        self.slack_client.rtm_connect()

        self.plugins = []
        self.load_plugins()

    def crons(self):
        for plugin in self.plugins:
            plugin.cron()

    def input(self, data):
        print data
        if 'type' in data:
            function_name = 'process_' + data['type']
            for plugin in self.plugins:
                plugin.register_cron()
                plugin.input(function_name, data)

    def load_plugins(self):
        for plugin in glob.glob(directory + '/plugins/*'):
            sys.path.insert(0, plugin)
            sys.path.insert(0, directory + '/plugins/')

        for plugin in glob.glob(directory + '/plugins/*.py') + \
                glob.glob(directory + '/plugins/*/*.py'):
            name = plugin.split('/')[-1][:-3]
            self.plugins.append(Plugin(name))

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

            self.crons()
            self.output()
            self.keepalive()
            time.sleep(.1)


class Job(object):
    def __init__(self, interval, function):
        self.function = function
        self.interval = interval
        self.lastrun = 0

    def __str__(self):
        return '%s %s %s' % (self.function, self.interval, self.lastrun)

    def __repr__(self):
        return self.__str__()

    def check(self):
        if self.lastrun + self.interval < time.time():
            self.function()
            self.lastrun = time.time()


class Plugin(object):
    def __init__(self, name):
        self.jobs = []
        self.module = __import__(name)
        self.name = name
        self.outputs = []
        self.register_cron()

        if 'setup' in dir(self.module):
            self.module.setup()

    def register_cron(self):
        if 'crontable' in dir(self.module):
            for interval, function in self.module.crontable:
                self.jobs.append(Job(interval,
                                     eval('self.module.%s' % function)))
            self.module.crontable = []
        else:
            self.module.crontable = []

    def input(self, function_name, data):
        if function_name in dir(self.module):
            eval('self.module.%s' % function_name)(data)

        if 'catch_all' in dir(self.module):
            self.module.catch_all(data)

    def cron(self):
        for job in self.jobs:
            job.check()

    def output(self):
        output = []
        while True:
            if 'outputs' in dir(self.module):
                if len(self.module.outputs) > 0:
                    output.append(self.module.outputs.pop(0))
                else:
                    break
            else:
                self.module.outputs = []

        return output


if __name__ == '__main__':
    directory = os.path.dirname(os.path.realpath(__name__))

    bot = Jarvis(os.environ['SLACK_TOKEN'])

    site_plugins = []
    files_currently_downloading = []
    job_hash = {}

    try:
        if DAEMON:
            import daemon

            with daemon.DaemonContext():
                bot.run()

        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)

