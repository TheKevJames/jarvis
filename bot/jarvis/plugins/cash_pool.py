"""
You can ask me to "show the cash pool" if you would like to see the debts. You
can also ask me to "show the cash pool's history", for an accounting of recent
transactions. Though I'll only show the most recent transactions by default, I
am able to "show the cash pool's entire history" on demand.

Alternatively, you may inform me that "Tom sent $42 to Dick" or that "Tom paid
$333 for Tom, Dick, and Harry". When away from home, do be more specific: when
in America, you should inform me that "Tom sent $42 USD to Dick."

You can ask me to "revert my last cash pool change" if you make a mistake. Of
course, I'll only let you revert your own changes.

If you're curious as to which "currencies are supported" or what my "default
currency" is, do let me know.
"""
import csv
import os
import time

import jarvis.db.dal as dal
import jarvis.db.users as users
import jarvis.core.helper as helper
import jarvis.core.messages as messages
import jarvis.core.plugin as plugin


CURRENCIES = ['CAD', 'USD']
DEFAULT_CURRENCY = CURRENCIES[0]


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


class CashPool(plugin.Plugin):
    def __init__(self, slack):
        super(CashPool, self).__init__(slack, 'cash_pool')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_message(r'(.*cash pool.*history.*)')
    def show_history(self, ch, _user, groups):
        history = CashPoolHistoryDal.read()
        if not history:
            self.send(ch, messages.NO_RECORD('cash pool'))
            return

        get_csv = any('csv' in g for g in groups)
        csv_file = 'cash_pool_output.csv'
        entire = any('entire' in g for g in groups)

        if get_csv:
            self.send_now(ch, messages.ACKNOWLEDGE())

            with open(csv_file, 'wb') as f:
                writer = csv.writer(f)
                writer.writerow(CashPoolHistoryDal.columns)
        elif entire:
            self.send(ch, messages.DISPLAYING('history'))
        else:
            self.send(ch, messages.DISPLAYING('recent history'))

        lookup = users.UsersDal.read_lookup_table()

        recent = None if entire else -10
        for item in history[recent:]:
            source, targets, value, currency, reason, user, date = item
            targets = eval(targets)  # pylint: disable=W0123
            if reason == 'REVERT':
                reason = '[REVERTED BY {}]'.format(lookup[user])

            if get_csv:
                with open(csv_file, 'ab') as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [lookup[source], [str(lookup[k]) for k in targets],
                         value, currency.upper(), reason, lookup[user], date])
                continue

            self.send(ch, messages.SHOW_CASH_POOL_HISTORY_ITEM(
                lookup[source], ' and '.join(lookup[k] for k in targets),
                value, currency.upper(), reason, lookup[user], date))

        if get_csv:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            self.upload_now(
                ch, 'Cash Pool History for {}'.format(current_time), csv_file,
                'csv')

            os.remove(csv_file)

    @plugin.Plugin.on_message(r'.*(display|show).*cash pool.*')
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

    @plugin.Plugin.on_message(
        r'(.*) (\w+) (sent|paid) \$([\d\.]+) ?(|{}) '
        r'(to|for) ([, \w]+)\.?'.format('|'.join(CURRENCIES).lower()))
    def send_cash(self, ch, user, groups):
        reason, single, _direction, value, currency, _, multiple = groups
        reason = reason[6:] if reason.startswith('jarvis') else reason
        if not currency:
            currency = DEFAULT_CURRENCY.lower()

        single = user if single == 'i' else users.UsersDal.read_by_name(single)

        multiple = helper.language_to_list(multiple)
        for idx, item in enumerate(multiple):
            if item == 'me':
                multiple[idx] = user
            elif item in ('herself', 'himself'):
                multiple[idx] = single
            else:
                multiple[idx] = users.UsersDal.read_by_name(item)

        CashPoolDal.update(single, multiple, int(float(value) * 100), currency)
        CashPoolHistoryDal.create(single, str(multiple), value, currency,
                                  reason.strip(' ,.?!'), user)

        self.send(ch, messages.ACKNOWLEDGE())

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

    @plugin.Plugin.on_message(r'.*revert my .*cash pool change.*')
    def revert_own_change(self, ch, user, _groups):
        if not self.revert_user_change(user):
            self.send(ch, messages.NO_REVERTABLE())
            return

        self.send(ch, messages.CLEANED_UP())

    @plugin.Plugin.require_auth
    @plugin.Plugin.on_message(r'.*revert the .*cash pool change.*')
    def revert_any_change(self, ch, _user, _groups):
        user = CashPoolHistoryDal.read_most_recent_user()
        if not user:
            self.send(ch, messages.NO_USAGE())
            return

        if not self.revert_user_change(user):
            self.send(ch, messages.NO_REVERTABLE())
            return

        self.send(ch, messages.CLEANED_UP())

    @plugin.Plugin.on_message(r'.*currencies.*support(ed)?.*')
    def get_all_currencies(self, ch, _user, _groups):
        supported = helper.list_to_language(CURRENCIES[:])
        self.send(ch, messages.SUPPORT(supported))

    @plugin.Plugin.on_message(r'.*default.*currency.*')
    def get_default_currency(self, ch, _user, _groups):
        self.send(ch, messages.DEFAULT_CURRENCY(DEFAULT_CURRENCY))
