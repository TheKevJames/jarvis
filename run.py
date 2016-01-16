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
                    filename='jarvis.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s')

log = logging.getLogger('requests')
log.setLevel(logging.WARNING)


def main(bot):
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info('Caught KeyboardInterrupt, shutting down.')
        ch = bot.slack.server.channels.find('D0ATCUTN1')
        if ch:
            msg = 'I actually think I need to sleep now, sir.'.encode('ascii',
                                                                      'ignore')
            ch.send_message('{}'.format(msg))

        sys.exit(0)
    except Exception as e:
        logger.error('Error running JARVIS.')
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
        robot = jarvis.Jarvis(token)
    except Exception as e:
        logger.error('Error initializing JARVIS.')
        logger.exception(e)
        sys.exit(-1)

    if arguments.get('--init'):
        robot.init()

    main(robot)
