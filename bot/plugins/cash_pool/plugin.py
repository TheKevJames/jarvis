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
import time

import jarvis.core.helper as helper
import jarvis.core.plugin as plugin
import jarvis.db.users as users

from .constant import ACKNOWLEDGE
from .constant import ALL_SETTLED
from .constant import ANALYZED
from .constant import CLEANED_UP
from .constant import CURRENCIES_MSG
from .constant import DEFAULT_CURRENCY_MSG
from .constant import NO_REVERTABLE
from .constant import NO_USAGE
from .constant import REGEX_CURRENCY
from .constant import REGEX_PAID_ONE
from .constant import REGEX_SENT_ONE
from .constant import SHOW_CASH_POOL_ITEM
from .dal import CashPoolDal
from .dal import CashPoolHistoryDal
from .helper import CashPoolHelper


class CashPool(plugin.Plugin):
    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    @plugin.Plugin.on_words({'cash pool', 'csv', 'history'})
    def show_history_csv(self, ch, _user, _groups):
        history = CashPoolHistoryDal.read()
        if not history:
            self.send(ch, NO_USAGE())
            return

        self.send_now(ch, ACKNOWLEDGE())

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
            self.send(ch, NO_REVERTABLE)
            return

        self.send(ch, CLEANED_UP())

    @plugin.Plugin.require_auth
    @plugin.Plugin.on_words(['revert', 'cash pool', 'change'])
    def revert_any_change(self, ch, _user, _groups):
        user = CashPoolHistoryDal.read_most_recent_user()
        if not user:
            self.send(ch, NO_USAGE())
            return

        if not CashPoolHelper.revert_user_change(user[0]):
            self.send(ch, NO_REVERTABLE)
            return

        self.send(ch, CLEANED_UP())

    @plugin.Plugin.on_words({'cash pool'})
    def show_pool(self, ch, _user, _groups):
        self.send(ch, ANALYZED)

        data = CashPoolDal.read()
        for first_name, cad, usd in data:
            if cad:
                self.send(ch, SHOW_CASH_POOL_ITEM(
                    first_name.title(), 'owes' if cad > 0 else 'is owed',
                    abs(cad), 'CAD'))
            if usd:
                self.send(ch, SHOW_CASH_POOL_ITEM(
                    first_name.title(), 'owes' if usd > 0 else 'is owed',
                    abs(usd), 'USD'))

        if not data:
            self.send(ch, ALL_SETTLED)

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
        self.send(ch, DEFAULT_CURRENCY_MSG)

    @plugin.Plugin.on_words({'currencies', 'support'})
    def get_all_currencies(self, ch, _user, _groups):
        self.send(ch, CURRENCIES_MSG)
