import re
import sys

import jarvis.core.messages as messages


DELIMITED = re.compile(r"[\w']+")


def get_channel_or_fail(logger, slack, channel):
    ch = slack.server.channels.find(channel)
    if not ch:
        logger.error(messages.NO_CHANNEL_FOUND(channel))
        sys.exit(1)

    return ch


def get_user_fields(slack, user):
    uuid = user['id']
    first_name = user['profile']['first_name'].lower()
    last_name = user['profile']['last_name'].lower()
    email = user['profile']['email']
    username = user['name']
    is_admin = int(user['is_admin'])

    channel = slack.api_call('im.open', user=uuid)['channel']['id']
    return uuid, first_name, last_name, email, username, is_admin, channel


def human_time_to_actual(human):
    time, period = human.split(' ')
    hours, minutes = map(int, time.split(':'))
    return int(hours) + (12 if period.lower() == 'pm' else 0), int(minutes)


def language_to_list(items):
    return filter(lambda u: u != 'and', re.findall(DELIMITED, items))


def list_to_language(items):
    if len(items) > 2:
        for i in range(len(items) - 1):
            items[i] = items[i] + ','

    items.insert(-1, 'and')
    return ' '.join(items)
