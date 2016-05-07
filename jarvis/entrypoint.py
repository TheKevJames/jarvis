import logging
import os
import sys

from jarvis import Jarvis


TOKEN = os.environ.get('SLACK_TOKEN', 'no-token')


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s (%(levelname)s): %(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)


def init():
    Jarvis(TOKEN).init()


def run():
    Jarvis(TOKEN).run()


def update():
    Jarvis(TOKEN).update()
