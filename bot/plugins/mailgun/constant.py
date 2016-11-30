MAIL_ERROR = 'Sir, there appears to be a problem with your mail server.'

BOUNCED = (MAIL_ERROR + ' A message sent from {} to {} has been bounced. ' + \
    'The SMTP server reports the following error: {}.').format
COMPLAINED = (MAIL_ERROR + ' A message sent from {} to {} has been '
                           'marked as spam.').format
DROPPED = (MAIL_ERROR + ' A message sent from {} to {} has been dropped. ' + \
    'Mailgun reports it is "{}".').format
