from collections import defaultdict
import cPickle as pickle
import re


crontable = []
outputs = []


SENT = re.compile(r'jarvis.* (\w+) sent \$([\d\.]+) to (\w+)', re.IGNORECASE)
PAID = re.compile(r'jarvis.* (\w+) paid \$([\d\.]+) for ([ \w]+)',
                  re.IGNORECASE)


PICKLE_FILE = 'cash_pool.pickle'
try:
    pool = pickle.load(open(PICKLE_FILE, 'rb'))
except IOError:
    pool = defaultdict(int)


def process_message(data):
    if 'text' in data:
        text = data['text'].lower()
        if not text.startswith('jarvis'):
            return


        if 'show the cash pool' in text:
            owes, owed = dict(), dict()
            for person, value in pool.iteritems():
                if value > 0:
                    owes[person] = value
                elif value < 0:
                    owed[person] = -value

            outputs.append([data['channel'], "I've analyzed your cash pool."])
            for person, value in sorted(owes.iteritems()):
                outputs.append([data['channel'],
                                '%s owes $%s' % (person.title(), value)])

            for person, value in sorted(owed.iteritems()):
                outputs.append([data['channel'],
                                '%s is owed $%s' % (person.title(), value)])

            return


        did_send = SENT.match(text)
        if did_send:
            sender, value, sendee = did_send.groups()
            sender = sender.lower()
            sendee = sendee.lower()
            value = float(value)

            pool[sender] -= value
            pool[sendee] += value

            pickle.dump(pool, open(PICKLE_FILE, 'wb'))
            return

        did_pay = PAID.match(text)
        if did_pay:
            payer, value, payees = did_pay.groups()
            payer = payer.lower()
            payees = payees.lower().split(' and ')
            value = float(value)
            num_payees = len([x for x in payees if x != payer])

            pool[payer] -= value * num_payees / (num_payees + 1)
            for payee in payees:
                pool[payee] += value / (num_payees + 1)

            pickle.dump(pool, open(PICKLE_FILE, 'wb'))
            return

