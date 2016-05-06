import sys

from jarvis.core.messages import NO_CHANNEL_FOUND


def get_channel_or_fail(logger, slack, channel):
    ch = slack.server.channels.find(channel)
    if not ch:
        logger.error(NO_CHANNEL_FOUND.format(channel))
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
