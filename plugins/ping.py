crontable = []
outputs = []


def process_message(data):
    if 'text' in data:
        text = data['text'].lower()
        if not text.startswith('jarvis'):
            return

        if 'you there?' in text:
            outputs.append([data['channel'], 'Oh hello, sir!'])
        elif "i'm back" in text:
            outputs.append([data['channel'], 'Welcome home, sir...'])


outputs.append(['D0ATCUTN1', 'J.A.R.V.I.S. online.'])
