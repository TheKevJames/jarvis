"""
I am version 0.3 of the J.A.R.V.I.S. natural language interface for Slack,
configured to perform a multitude of functions.
"""
crontable = []
outputs = []


def process_message(data):
    if 'you there?' in data['text']:
        outputs.append([data['channel'], 'Oh hello, sir!'])
    elif 'you up?' in data['text']:
        outputs.append([data['channel'], 'At your service, sir.'])
    elif "i'm back" in data['text']:
        outputs.append([data['channel'], 'Welcome home, sir...'])
    elif 'describe yourself' in data['text']:
        outputs.append([data['channel'], __doc__.replace('\n', ' ')])


outputs.append(['D0ATCUTN1', 'J.A.R.V.I.S. online.'])
