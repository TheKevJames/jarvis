"""
You can ask me to "show the cash pool" if you would like to see the debts. You
can also ask me to "show the cash pool's history", for an accounting of recent
transactions. Though I'll only show the most recent transactions by default, I
am able to "show the cash pool's entire history" on demand.

Alternatively, you may inform me that "Tom sent $42 to Dick" or that "Tom paid
$333 for Tom, Dick, and Harry". When away from home, do be more specific: when
in America, you should inform me that "Tom sent $42 USD to Dick."

I should also be able to understand more complex information, such as in the
case where bill is split inequally or multiple people pay for portions of the
bill. Maybe "Tom paid $20 USD and Dick paid $80 CAD for Tom, Dick, and Harry."
or "Tom paid $40 for Dick and Tom paid $120 for Tom and Harry."

You can ask me to "revert my last cash pool change" if you make a mistake. Of
course, I'll only let you revert your own changes. Only administrators can
revert other people's changes.

If you're curious as to which "currencies are supported" or what my "default
currency" is, do let me know.
"""
import csv
import os
import re
import time

import jarvis.db.dal as dal
import jarvis.db.users as users
import jarvis.core.helper as helper
import jarvis.core.messages as messages
import jarvis.core.plugin as plugin


CURRENCIES = ['CAD', 'USD']
DEFAULT_CURRENCY = CURRENCIES[0]

REGEX_CURRENCY = r'\$([\d\.]+) ?(|{})'.format('|'.join(CURRENCIES).lower())
REGEX_PAID_ONE = re.compile(
    r'(\w+) paid {} for ([ \w]+)'.format(REGEX_CURRENCY))
REGEX_SENT_ONE = re.compile(r'(\w+) sent {} to (\w+)'.format(REGEX_CURRENCY))


class CashPoolDal(dal.Dal):
    # pylint: disable=E0213
    def read(cur):
        return cur.execute(""" SELECT first_name,
                                      CAST(cad AS FLOAT) / 100,
                                      CAST(usd AS FLOAT) / 100
                               FROM cash_pool
                               INNER JOIN user
                                   ON user.uuid = cash_pool.uuid
                               WHERE cad <> 0 OR usd <> 0
                               ORDER BY first_name ASC
                           """).fetchall()

    ensure = 'INSERT OR IGNORE INTO cash_pool(uuid) VALUES(?)'
    update_by_currency_dec = 'UPDATE cash_pool SET {} = {} - ? WHERE uuid = ?'
    update_by_currency_inc = 'UPDATE cash_pool SET {} = {} + ? WHERE uuid = ?'

    def update(cur, source, targets, value, currency):
        dec = CashPoolDal.update_by_currency_dec.format(currency, currency)
        inc = CashPoolDal.update_by_currency_inc.format(currency, currency)

        cur.execute(CashPoolDal.ensure, [source])
        cur.execute(dec, [value, source])
        for target in targets:
            target_value = int(round(value / len(targets)))
            cur.execute(CashPoolDal.ensure, [target])
            cur.execute(inc, [target_value, target])


class CashPoolHistoryDal(dal.Dal):
    # pylint: disable=E0213
    columns = ['source', 'targets', 'value', 'currency', 'reason',
               'created_by']

    def create(cur, source, targets, value, currency, reason, user):
        cur.execute(""" INSERT INTO cash_pool_history (source, targets,
                                                       value, currency,
                                                       reason, created_by)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, [source, targets, value, currency, reason, user])

    def read(cur):
        return cur.execute(""" SELECT source, targets, value, currency,
                                      reason, created_by, created_at
                               FROM cash_pool_history
                               ORDER BY created_at ASC
                           """).fetchall()

    def read_most_recent_by_user(cur, user):
        return cur.execute(""" SELECT source, targets, value, currency
                               FROM cash_pool_history
                               WHERE created_by = ?
                               ORDER BY created_at DESC
                               LIMIT 1
                           """, [user]).fetchone()

    def read_most_recent_user(cur):
        return cur.execute(""" SELECT created_by
                               FROM cash_pool_history
                               ORDER BY created_at DESC
                               LIMIT 1
                           """).fetchone()


class CashPoolHelper:
    @staticmethod
    def do_transactions(send, ch, user, reason, transactions, regex):
        for tx in transactions:
            sender, value, curr, receiver = regex.match(tx).groups()
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

            send(ch, messages.ACKNOWLEDGE())

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
            send(ch, messages.CONFUSED())
            return list()

        # ensure all chunks have receiver info
        if receiver_count == 1:
            if word not in chunks[-1].split(' '):
                send(ch, messages.CONFUSED())
                return list()

            receiver = chunks[-1][chunks[-1].index(word)-1:]
            for i, _ in enumerate(chunks[:-1]):
                chunks[i] += receiver

        return chunks

    @staticmethod
    def get_real_receiver(send, ch, user, sender, receiver):
        try:
            return users.UsersDal.read_by_name(receiver)
        except TypeError:
            if receiver not in ('me', 'himself', 'herself'):
                send(ch, messages.NO_USER(receiver))
                return

            if receiver == 'me':
                return user
            if receiver in ('himself', 'herself'):
                return sender

    @staticmethod
    def get_real_sender(send, ch, user, sender):
        try:
            return users.UsersDal.read_by_name(sender)
        except TypeError:
            if sender != 'i':
                send(ch, messages.NO_USER(sender))
                return

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
            send(ch, messages.NO_RECORD('cash pool'))
            return

        send(ch, messages.DISPLAYING(message))

        lookup = users.UsersDal.read_lookup_table()
        for item in history[-limit:]:
            source, targets, value, currency, reason, user, date = item
            targets = eval(targets)  # pylint: disable=W0123
            if reason == 'REVERT':
                reason = '[REVERTED BY {}]'.format(lookup[user])

            send(ch, messages.SHOW_CASH_POOL_HISTORY_ITEM(
                lookup[source], ' and '.join(lookup[k] for k in targets),
                value, currency.upper(), reason, lookup[user], date))

    @staticmethod
    def revert_user_change(user):
        last = CashPoolHistoryDal.read_most_recent_by_user(user)
        if not last:
            return False

        source, targets, value, currency = last
        CashPoolDal.update(source, eval(targets),  # pylint: disable=W0123
                           -int(float(value) * 100), currency)
        CashPoolHistoryDal.create(source, targets, value, currency, 'REVERT',
                                  user)

        return True


class CashPool(plugin.Plugin):
    def __init__(self, slack):
        super().__init__(slack, 'cash_pool')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_words({'cash pool', 'csv', 'history'})
    def show_history_csv(self, ch, _user, _groups):
        history = CashPoolHistoryDal.read()
        if not history:
            self.send(ch, messages.NO_RECORD('cash pool'))
            return

        self.send_now(ch, messages.ACKNOWLEDGE())

        csv_file = 'cash_pool_history.csv'
        with open(csv_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(CashPoolHistoryDal.columns)

        lookup = users.UsersDal.read_lookup_table()
        for item in history:
            source, targets, value, currency, reason, user, date = item
            targets = eval(targets)  # pylint: disable=W0123
            if reason == 'REVERT':
                reason = '[REVERTED BY {}]'.format(lookup[user])

            with open(csv_file, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(
                    [lookup[source], [str(lookup[k]) for k in targets],
                     value, currency.upper(), reason, lookup[user], date])

        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.upload_now(
            ch, 'Cash Pool History for {}'.format(current_time), csv_file,
            'csv')

        os.remove(csv_file)

    @plugin.Plugin.on_words({'cash pool', 'entire', 'history'})
    def show_history_entire(self, ch, _user, _groups):
        CashPoolHelper.print_history(self.send, ch, 'history')

    @plugin.Plugin.on_words({'cash pool', 'history'})
    def show_history(self, ch, _user, _groups):
        CashPoolHelper.print_history(self.send, ch, 'recent history', limit=10)

    @plugin.Plugin.on_words(['revert', 'my', 'cash pool', 'change'])
    def revert_own_change(self, ch, user, _groups):
        if not CashPoolHelper.revert_user_change(user):
            self.send(ch, messages.NO_REVERTABLE())
            return

        self.send(ch, messages.CLEANED_UP())

    @plugin.Plugin.require_auth
    @plugin.Plugin.on_words(['revert', 'cash pool', 'change'])
    def revert_any_change(self, ch, _user, _groups):
        user = CashPoolHistoryDal.read_most_recent_user()
        if not user:
            self.send(ch, messages.NO_USAGE())
            return

        if not CashPoolHelper.revert_user_change(user[0]):
            self.send(ch, messages.NO_REVERTABLE())
            return

        self.send(ch, messages.CLEANED_UP())

    @plugin.Plugin.on_words({'cash pool'})
    def show_pool(self, ch, _user, _groups):
        self.send(ch, messages.ANALYZED_CASH_POOL())

        data = CashPoolDal.read()
        for first_name, cad, usd in data:
            if cad:
                self.send(ch, messages.SHOW_CASH_POOL_ITEM(
                    first_name.title(), 'owes' if cad > 0 else 'is owed',
                    abs(cad), 'CAD'))
            if usd:
                self.send(ch, messages.SHOW_CASH_POOL_ITEM(
                    first_name.title(), 'owes' if usd > 0 else 'is owed',
                    abs(usd), 'USD'))

        if not data:
            self.send(ch, messages.ALL_SETTLED())

    @plugin.Plugin.on_regex(r'(.*paid {} for.*)'.format(REGEX_CURRENCY))
    def do_payment(self, ch, user, groups):
        chunks = helper.sentence_to_chunks(groups[0].replace('jarvis', ''))

        chunks, reason = CashPoolHelper.extract_reason(chunks, word='paid')

        # allow multiple receivers
        # NOTE: using 'for' interferes with reason extraction, this must not be
        # first
        chunks = CashPoolHelper.merge_nameonly_chunks(
            chunks, words=('paid', 'for'))

        chunks = CashPoolHelper.fixup_receivers(
            self.send, ch, chunks, word='for')

        CashPoolHelper.do_transactions(
            self.send, ch, user, reason, chunks, REGEX_PAID_ONE)

    @plugin.Plugin.on_regex(r'(.*sent {} to.*)'.format(REGEX_CURRENCY))
    def do_send(self, ch, user, groups):
        chunks = helper.sentence_to_chunks(groups[0].replace('jarvis', ''))

        chunks, reason = CashPoolHelper.extract_reason(chunks, word='sent')

        chunks = CashPoolHelper.fixup_receivers(
            self.send, ch, chunks, word='to')

        CashPoolHelper.do_transactions(
            self.send, ch, user, reason, chunks, REGEX_SENT_ONE)

    @plugin.Plugin.on_words({'currency', 'default'})
    def get_default_currency(self, ch, _user, _groups):
        self.send(ch, messages.DEFAULT_CURRENCY(DEFAULT_CURRENCY))

    @plugin.Plugin.on_words({'currencies', 'support'})
    def get_all_currencies(self, ch, _user, _groups):
        supported = helper.list_to_language(CURRENCIES[:])
        self.send(ch, messages.SUPPORT(supported))
