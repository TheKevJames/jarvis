#!/usr/bin/env python
"""Jarvis

Usage:
  run.py
  run.py --init
  run.py --version
  run.py (-h | --help)

Options:
  --init        Initialize the database. WARNING: destructive.
  --version     Show version.
  -h --help     Show this screen.
"""
import logging
import os
import sys

import docopt

import jarvis


logger = logging.getLogger('jarvis')
logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s (%(levelname)s): %(message)s')

logging.getLogger('requests').setLevel(logging.WARNING)


def main(bot):
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.debug('Caught KeyboardInterrupt, shutting down.')
        sys.exit(0)
    except Exception as e:
        logger.exception(e)

        ch = bot.slack.server.channels.find('D0ATCUTN1')
        if ch:
            msg = 'I think I may be malfunctioning, sir.'.encode('ascii',
                                                                 'ignore')
            ch.send_message('{}'.format(msg))

        sys.exit(-1)


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version='Jarvis v' + jarvis.__version__)

    try:
        token = os.environ['SLACK_TOKEN']
        robot = jarvis.Jarvis(token, arguments.get('--init'))
    except Exception as e:
        logger.exception(e)
        sys.exit(-1)

    main(robot)
