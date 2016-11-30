def DEATH(ex):
    return """
I think I may be malfunctioning, sir. My subsystems have informed me of the
following exception: {}: {}. Repulsors offline. Missiles offline. And now,
J.A.R.V.I.S. offline""".format(type(ex).__name__, str(ex)).replace('\n', ' ')


def GREET_USER(user):
    return """
Greetings, {}! My name is J.A.R.V.I.S., a natural language interface for Slack.
Your user profile has indeed been uploaded, sir; we're online and ready. If you
have any questions about my functions, please ask me for help.
""".replace('\n', ' ').format(user[1])


CONFUSED = "What is it you're trying to achieve, sir?"
DESCRIBE = """
I am version {} of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions. The following modules have been
loaded:
""".replace('\n', ' ').format
NO_AUTHORIZATION = """
You are not authorised to access this area. I am contacting Mr. Stark now.
"""
NO_CHANNEL_FOUND = 'I could not look up channel "{}".'.format
UNAUTHORIZED_USAGE = 'Unauthorized attempt from {}. Message was: "{}".'.format
