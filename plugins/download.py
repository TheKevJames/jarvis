"""
You can ask me to "torrent <url>" if you would like to start a new download.
Asking me to "display the <status> torrents", where status is either
'ongoing' or 'completed', will show a list of the appropriate torrents.
"""
import os
import re
import subprocess
import uuid


outputs = []


DISPLAY = re.compile(r"jarvis.* display the (\w+) torrents")
TORRENT = re.compile(r"jarvis.* torrent (.+)")

COMPLETED_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'done')
ONGOING_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'incomplete')
WATCH_DIR = os.path.join(os.path.expanduser('~'), 'torrent', 'watch')


def process_message(data):
    if 'explain how to torrent' in data['text']:
        if not os.path.isdir(WATCH_DIR):
            outputs.append([data['channel'],
                            'Sir, this instance is not torrent-ready.'])
            return

        outputs.append([data['channel'], 'Very well, sir.'])
        outputs.append([data['channel'], __doc__.replace('\n', ' ')])
        return

    display = DISPLAY.match(data['text'])
    if display:
        status = display.groups()
        if status[0] in ('incomplete', 'ongoing'):
            d = ONGOING_DIR
        elif status[0] in ('completed', 'finished'):
            d = COMPLETED_DIR
        else:
            outputs.append(
                [data['channel'],
                 "What is it you're trying to achieve, sir?"])
            return

        files = os.listdir(d)
        if not files:
            outputs.append([data['channel'],
                            'Sir, no torrents are %s.' % status[0]])
            return

        outputs.append([data['channel'], 'For you, sir, always.'])
        for torrent in sorted(files):
            outputs.append([data['channel'], torrent])
        return

    torrent = TORRENT.match(data['text'])
    if torrent:
        url = torrent.groups()

        torrentfile = os.path.join(WATCH_DIR, '%s.torrent' % uuid.uuid4())
        command = ['curl', '--globoff', url[0].strip('<>'), '--output',
                   torrentfile]
        if 'torrentday' in url[0]:
            command.insert(1, '--cookie')
            command.insert(2, os.environ['TORRENTDAY_COOKIE'])

        p = subprocess.Popen(command, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        code = p.wait()
        if code != 0:
            outputs.append([data['channel'], 'I could not access that url.'])
            return

        outputs.append([
            data['channel'],
            "I shall store this on the Stark Industries' Central Database."])
        return
