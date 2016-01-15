class Plugin(object):
    def __init__(self, slack):
        self.slack = slack

    # TODO: buffer, send in one message
    @staticmethod
    def send(channel, message):
        channel.send_message(message.encode('ascii', 'ignore'))

    def respond(self, ch=None, user=None, msg=None):
        raise NotImplementedError
