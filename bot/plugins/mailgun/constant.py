import random


def ACKNOWLEDGE():
    return random.choice(('As you wish.', 'Check.', 'Very good, sir.',
                          'Yes, sir.'))


def APOLOGIZE():
    return random.choice(('My apologies, sir.', 'Sorry, sir.'))


ALREADY_FOLLOWING = lambda x: \
    APOLOGIZE() + ' I already knew you used {}.'.format(x)
CREATED_FOLLOW = lambda x: \
    ACKNOWLEDGE() + ' You will now receive updates about {}.'.format(x)
DELETED_FOLLOW = lambda x: \
    ACKNOWLEDGE() + ' You will no longer see notifications for {}.'.format(x)

MAIL_ERROR = 'Sir, there appears to be a problem with your mail server.'

BOUNCED = (MAIL_ERROR + ' A message sent via {} to {} has been bounced. ' + \
    'The SMTP server reports the following error: {}.').format
COMPLAINED = (MAIL_ERROR + ' A message sent via {} to {} has been '
                           'marked as spam.').format
DROPPED = (MAIL_ERROR + ' A message sent via {} to {} has been dropped. ' + \
    'Mailgun reports it is "{}".').format
