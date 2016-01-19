"""
You can ask me to "torrent <url>" if you would like to start a new download.
Asking me to "display the <status> torrents", where status is either
'ongoing' or 'completed', will show a list of the appropriate torrents.
"""
import os
import re
import subprocess
import uuid

from ..plugin import Plugin


DISPLAY = re.compile(r"jarvis.* display the (\w+) torrents")
TORRENT = re.compile(r"jarvis.* torrent (.+)")

COMPLETED_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'done')
ONGOING_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'incomplete')
WATCH_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'watch')


class Download(Plugin):
    def __init__(self, slack):
        super(Download, self).__init__(slack, 'download')

    def help(self, ch):
        if not os.path.isdir(WATCH_DIR):
            self.send(ch, 'Sir, this instance is not torrent-ready.')
            return

        self.send(ch, __doc__.replace('\n', ' '))

    def respond(self, ch=None, user=None, msg=None):
        display = DISPLAY.match(msg)
        if display:
            status = display.groups()
            if status[0] in ('incomplete', 'ongoing'):
                target_directory = ONGOING_DIR
            elif status[0] in ('completed', 'finished'):
                target_directory = COMPLETED_DIR
            else:
                self.send(ch, "What is it you're trying to achieve, sir?")
                return

            files = os.listdir(target_directory)
            if not files:
                self.send(ch, 'Sir, no torrents are {}.'.format(status[0]))
                return

            message = ['For you, sir, always.']
            for torrent in sorted(files):
                message.append(torrent)

            self.send(ch, '\n'.join(message))
            return

        torrent = TORRENT.match(msg)
        if torrent:
            url = torrent.groups()

            torrentfile = os.path.join(WATCH_DIR,
                                       '{}.torrent'.format(uuid.uuid4()))
            command = ['curl', '--globoff', url[0].strip('<>'), '--output',
                       torrentfile]
            if 'torrentday' in url[0]:
                command.insert(1, '--cookie')
                command.insert(2, os.environ['TORRENTDAY_COOKIE'])

            p = subprocess.Popen(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            code = p.wait()
            if code != 0:
                self.send(ch, 'I could not access that url.')
                return

            self.send(ch,
                      "I shall store this on the Stark Industries' "
                      "Central Database.")
