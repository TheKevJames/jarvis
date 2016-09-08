import logging
import os

from jarvis import Jarvis


TOKEN = os.environ['SLACK_TOKEN']


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s (%(levelname)s): %(message)s')
logging.getLogger('requests').setLevel(logging.WARNING)


def init():
    Jarvis(TOKEN).init()


def run():
    Jarvis(TOKEN).run()
