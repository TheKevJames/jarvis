#!/usr/bin/env python
import logging
import os
import sys

import jarvis


logger = logging.getLogger('jarvis')
logging.basicConfig(level=logging.DEBUG,
                    filename='jarvis.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s')

log = logging.getLogger('requests')
log.setLevel(logging.WARNING)


def main():
    try:
        token = os.environ['SLACK_TOKEN']

        bot = jarvis.Jarvis(token)
    except Exception as e:
        logger.error('Error initializing JARVIS.')
        logger.exception(e)
        sys.exit(-1)

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
    main()
