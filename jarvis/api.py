import json


def build_user(slack, data):
    uuid = data['id']
    first_name = data['profile']['first_name'].lower()
    last_name = data['profile']['last_name'].lower()
    email = data['profile']['email']
    username = data['name']
    is_admin = int(data['is_admin'])

    channel = json.loads(slack.api_call('im.open', user=uuid))['channel']['id']

    return uuid, first_name, last_name, email, username, is_admin, channel
