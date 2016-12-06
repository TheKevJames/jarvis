import random


def ACKNOWLEDGE():
    return random.choice(('As you wish.', 'Check.', 'Very good, sir.',
                          'Yes, sir.'))


def APOLOGIZE():
    return random.choice(('My apologies, sir.', 'Sorry, sir.'))


ALREADY_FOLLOWING = lambda x: \
    APOLOGIZE() + ' You are already following {}.'.format(x)
CREATED_FOLLOW = lambda x: \
    ACKNOWLEDGE() + ' You are now registered for updates about {}.'.format(x)
DELETED_FOLLOW = lambda x: \
    ACKNOWLEDGE() + ' You are no longer registered for {} updates.'.format(x)
UPDATED_USERNAME = lambda x: \
    ACKNOWLEDGE() + " I've recorded your Docker Hub username as {}.".format(x)

IMAGE_PUSHED = 'A new version of {} has been pushed to Docker Hub.'.format
