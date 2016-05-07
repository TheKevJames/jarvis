"""
You can ask me to "torrent <url>" if you would like to start a new download.
Asking me to "display the <status> torrents", where status is either
'ongoing' or 'completed', will show a list of the appropriate torrents.
"""
import os
import subprocess

import jarvis.core.messages as messages
import jarvis.core.plugin as plugin


COMPLETED_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'done')
ONGOING_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'incomplete')
WATCH_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'watch')


class Download(plugin.Plugin):
    def __init__(self, slack):
        super(Download, self).__init__(slack, 'download')

    def help(self, ch):
        if not os.path.isdir(WATCH_DIR):
            self.send_now(ch, messages.ERROR_NOT_ENABLED('torrent'))
            return

        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_message(r'.*display the (\w+) torrents.*')
    def display(self, ch, _user, groups):
        status = groups[0]
        if status in ('incomplete', 'ongoing'):
            target_directory = ONGOING_DIR
        elif status in ('completed', 'finished'):
            target_directory = COMPLETED_DIR
        else:
            self.send(ch, messages.CONFUSED())
            return

        files = os.listdir(target_directory)
        if not files:
            self.send(ch, 'Sir, no torrents are {}.'.format(status[0]))
            return

        self.send(ch, messages.ACKNOWLEDGE())
        for torrent in sorted(files):
            self.send(ch, torrent)

    @plugin.Plugin.on_message(r'.*torrent (.+)\.?')
    def download(self, ch, _user, groups):
        url = groups[0].strip('<>')

        torrentfile = os.path.join(WATCH_DIR, '{}.torrent'.format(url))
        command = ['curl', '--globoff', url, '--output', torrentfile]
        if 'torrentday' in url[0]:
            cookie = os.environ.get('TORRENTDAY_COOKIE')
            if not cookie:
                self.send(ch, messages.ERROR_NOT_ENABLED('torrent'))
                return

            command.insert(1, '--cookie')
            command.insert(2, cookie)

        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        code = p.wait()
        if code != 0:
            self.send(ch, messages.ERROR_ACCESS_URL())
            return

        self.send(ch, messages.WILL_STORE())
