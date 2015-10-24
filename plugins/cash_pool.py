"""
You can ask me to "show the cash pool" if you would like to see your debts. You
can also ask me to "show the cash pool history", if you'd prefer.
Alternatively, you may inform me that "Tom sent $42 to Dick" or that "Tom paid
$333 for Tom, Dick, and Harry".
"""
from collections import defaultdict
import cPickle as pickle
import re


outputs = []


SENT = re.compile(r'jarvis.* (\w+) sent \$([\d\.]+) to (\w+)')
PAID = re.compile(r'jarvis.* (\w+) paid \$([\d\.]+) for ([ \w]+)')


PICKLE_FILE = 'cash_pool.pickle'
try:
    pool = pickle.load(open(PICKLE_FILE, 'rb'))
except IOError:
    pool = defaultdict(int)

PICKLE_HISTORY_FILE = 'cash_pool_history.pickle'
try:
    history = pickle.load(open(PICKLE_HISTORY_FILE, 'rb'))
except IOError:
    history = list()


def show_history(channel, recent=None):
    if history:
        outputs.append([channel,
                        'Very good, sir, displaying your history now:'])
    else:
        outputs.append([channel, 'I have no record of a cash pool, sir.'])

    for line in history[recent:]:
        # TODO: better history sanitization
        outputs.append([channel, line.replace('jarvis, ', '')])

    return


def show_pool(channel):
    outputs.append([channel, "I've analyzed your cash pool."])
    for person, value in sorted(pool.iteritems()):
        outputs.append([channel,
                        '%s %s $%s' % (person.title(),
                                       'owes' if value > 0 else 'is owed',
                                       abs(value) / 100.)])


    if not pool:
        outputs.append([channel, 'All appears to be settled.'])


def process_message(data):
    if 'explain the cash pool' in data['text']:
        outputs.append([data['channel'], 'Very well, sir.'])
        outputs.append([data['channel'], __doc__.replace('\n', ' ')])
        return

    if 'show the cash pool' in data['text']:
        if 'history' in data['text']:
            if 'recent' in data['text']:
                show_history(data['channel'], recent=-10)
                return

            show_history(data['channel'])
            return

        show_pool(data['channel'])
        return

    did_send = SENT.match(data['text'])
    if did_send:
        sender, value, sendee = did_send.groups()
        value = int(float(value) * 100)

        pool[sender] -= value
        if not pool[sender]:
            del pool[sender]

        pool[sendee] += value
        if not pool[sendee]:
            del pool[sendee]

        history.append(data['text'])

        pickle.dump(history, open(PICKLE_HISTORY_FILE, 'wb'))
        pickle.dump(pool, open(PICKLE_FILE, 'wb'))

        outputs.append([data['channel'], 'Very good, sir.'])
        return

    did_pay = PAID.match(data['text'])
    if did_pay:
        payer, value, payees = did_pay.groups()
        payees = payees.split(' and ')
        value = int(float(value) * 100)

        pool[payer] -= value
        if not pool[payer]:
            del pool[payer]

        for payee in payees:
            pool[payee] += int(round(value / len(payees)))
            if not pool[payee]:
                del pool[payee]

        history.append(data['text'])

        pickle.dump(history, open(PICKLE_HISTORY_FILE, 'wb'))
        pickle.dump(pool, open(PICKLE_FILE, 'wb'))

        outputs.append([data['channel'], 'Very good, sir.'])
        return
