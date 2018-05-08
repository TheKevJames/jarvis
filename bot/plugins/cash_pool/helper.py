import jarvis.db.users as users

from .constant import ACKNOWLEDGE
from .constant import CONFUSED
from .constant import DEFAULT_CURRENCY
from .constant import DISPLAYING
from .constant import MALFORMED
from .constant import NO_USAGE
from .constant import NO_USER
from .constant import SHOW_CASH_POOL_HISTORY_ITEM
from .dal import CashPoolDal
from .dal import CashPoolHistoryDal


class CashPoolHelper:
    @staticmethod
    def do_transactions(send, ch, user, reason, transactions, regex):
        # pylint: disable=too-many-arguments
        for tx in transactions:
            try:
                sender, value, curr, receiver = regex.match(tx).groups()
            except AttributeError:
                # no match
                send(ch, MALFORMED(tx))
                return

            curr = curr or DEFAULT_CURRENCY.lower()
            receivers = receiver.split(' ')

            sender = CashPoolHelper.get_real_sender(send, ch, user, sender)
            if not sender:
                return

            for i, recv in enumerate(receivers):
                receivers[i] = CashPoolHelper.get_real_receiver(
                    send, ch, user, sender, recv)
                if not receivers[i]:
                    return

            CashPoolDal.update(sender, receivers, int(float(value)*100), curr)
            CashPoolHistoryDal.create(sender, str(receivers), value, curr,
                                      reason, user)

            send(ch, ACKNOWLEDGE())

    @staticmethod
    def extract_reason(message, word):
        if not message[0].startswith('for'):
            return message, ''

        split, idx = [], 0
        while word not in split:
            if split:
                split += ['and']
            split += message[idx].split(' ')
            idx += 1
        reason = ' '.join(split[:split.index(word) - 1])
        message = [' '.join(split).replace(reason, '').strip()] + message[idx:]
        return message, reason

    @staticmethod
    def fixup_receivers(send, ch, chunks, word):
        # ensure parseable receivers
        receiver_count = len([c for c in chunks if word in c.split(' ')])
        if receiver_count not in (1, len(chunks)):
            send(ch, CONFUSED)
            return list()

        # ensure all chunks have receiver info
        if receiver_count == 1:
            if word not in chunks[-1].split(' '):
                send(ch, CONFUSED)
                return list()

            receiver = chunks[-1][chunks[-1].index(word)-1:]
            for i, _ in enumerate(chunks[:-1]):
                chunks[i] += receiver

        return chunks

    @staticmethod
    def get_real_receiver(send, ch, user, sender, receiver):
        try:
            return users.UsersDal.read_by_name(receiver)[0]
        except TypeError:
            if receiver not in ('me', 'himself', 'herself'):
                send(ch, NO_USER(receiver))
                return None

            if receiver == 'me':
                return user
            if receiver in ('himself', 'herself'):
                return sender

    @staticmethod
    def get_real_sender(send, ch, user, sender):
        try:
            return users.UsersDal.read_by_name(sender)[0]
        except TypeError:
            if sender != 'i':
                send(ch, NO_USER(sender))
                return None

            return user

    @staticmethod
    def merge_nameonly_chunks(chunks, words):
        for i in range(len(chunks) - 1, -1, -1):
            if words[0] not in chunks[i] and words[1] not in chunks[i]:
                chunks[i-1] += ' ' + chunks[i]
                del chunks[i]

        return chunks

    @staticmethod
    def print_history(send, ch, message, limit=0):
        history = CashPoolHistoryDal.read()
        if not history:
            send(ch, NO_USAGE())
            return

        send(ch, DISPLAYING(message))

        lookup = users.UsersDal.read_lookup_table()
        for item in history[-limit:]:
            source, targets, value, currency, reason, user, date = item
            targets = eval(targets)  # pylint: disable=W0123
            if reason == 'REVERT':
                reason = '[REVERTED BY {}]'.format(lookup[user])

            send(ch, SHOW_CASH_POOL_HISTORY_ITEM(
                lookup[source], ' and '.join(lookup[k] for k in targets),
                value, currency.upper(), reason, lookup[user], date))

    @staticmethod
    def revert_user_change(user):
        last = CashPoolHistoryDal.read_most_recent_by_user(user)
        if not last:
            return False

        source, targets, value, currency = last
        # TODO: use a real data structure here
        CashPoolDal.update(source, eval(targets),  # pylint: disable=W0123
                           -int(float(value) * 100), currency)
        CashPoolHistoryDal.create(source, targets, value, currency, 'REVERT',
                                  user)

        return True
