crontable = []
outputs = []


def process_message(data):
    if 'you there?' in data['text'].lower():
        outputs.append([data['channel'], 'Oh hello, sir!'])


outputs.append(['D0ATCUTN1', 'J.A.R.V.I.S. online.'])
