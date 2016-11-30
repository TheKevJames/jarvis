"""
You can ask me to "torrent <url>" if you would like to start a new download.
Asking me to "display the <status> torrents", where status is either
'incomplete' or 'completed', will show a list of the appropriate torrents.
"""
import os
import subprocess

import jarvis.core.plugin as plugin

from .constant import ACQUIESE
from .constant import COMPLETED_DIR
from .constant import ERROR_ACCESSING_URL
from .constant import ERROR_NOT_ENABLED
from .constant import ONGOING_DIR
from .constant import WATCH_DIR
from .constant import WILL_STORE


class Download(plugin.Plugin):
    def help(self, ch):
        if not os.path.isdir(WATCH_DIR):
            self.send_now(ch, ERROR_NOT_ENABLED())
            return

        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_words({'display', 'incomplete', 'torrents'})
    def display_incomplete(self, ch, _user, _groups):
        files = os.listdir(ONGOING_DIR)
        if not files:
            self.send(ch, 'Sir, no torrents are incomplete.')
            return

        self.send(ch, ACQUIESE())
        for torrent in sorted(files):
            self.send(ch, torrent)

    @plugin.Plugin.on_words({'display', 'torrents'})
    def display(self, ch, _user, _groups):
        files = os.listdir(COMPLETED_DIR)
        if not files:
            self.send(ch, 'Sir, no torrents have finished downloading.')
            return

        self.send(ch, ACQUIESE())
        for torrent in sorted(files):
            self.send(ch, torrent)

    @plugin.Plugin.on_regex(r'.*torrent (.+)\.?')
    def download(self, ch, _user, groups):
        url = groups[0].strip('<>')

        torrentfile = os.path.join(WATCH_DIR, '{}.torrent'.format(url))
        command = ['curl', '--globoff', url, '--output', torrentfile]
        if 'torrentday' in url[0]:
            cookie = os.environ.get('TORRENTDAY_COOKIE')
            if not cookie:
                self.send(ch, ERROR_NOT_ENABLED())
                return

            command.insert(1, '--cookie')
            command.insert(2, cookie)

        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        code = p.wait()
        if code != 0:
            self.send(ch, ERROR_ACCESSING_URL)
            return

        self.send(ch, WILL_STORE)
