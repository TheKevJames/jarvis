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
import contextlib
import re

from ..db import conn
from ..plugin import Plugin


DELIMITED = re.compile(r"[\w']+")
CURRENCIES = ['CAD', 'USD']
DEFAULT_CURRENCY = CURRENCIES[0]


class CashPool(Plugin):
    def __init__(self, slack):
        super(CashPool, self).__init__(slack, 'cash_pool')

    def help(self, ch):
        self.send_now(ch, __doc__.replace('\n', ' '))

    # TODO: fix bug where large 'entire' history crashes Jarvis
    @Plugin.on_message(r'(.*cash pool.*history.*)')
    def show_history(self, ch, _user, groups):
        recent = -10
        if any('entire' in g for g in groups):
            recent = None

        with contextlib.closing(conn.cursor()) as cur:
            history = cur.execute(""" SELECT source, targets, value, currency,
                                             reason, created_by
                                      FROM cash_pool_history
                                      ORDER BY created_at ASC
                                  """).fetchall()
            lookup = {k: v for k, v in cur.execute(
                """ SELECT uuid, first_name FROM user """).fetchall()}

        if not history:
            self.send(ch, 'I have no record of a cash pool, sir.')
        elif recent is None:
            self.send(ch, 'Very good, sir, displaying your history now:')
        else:
            self.send(ch, 'Very good, sir, displaying recent history now:')

        for item in history[recent:]:
            source, targets, value, currency, reason, user = item
            targets = eval(targets)  # pylint: disable=W0123
            if reason == 'REVERT':
                reason = '[REVERTED BY {}]'.format(lookup[user])

            self.send(ch, '{} -> {}: ${} {} {}'.format(
                lookup[source], ' and '.join(lookup[k] for k in targets),
                value, currency.upper(), reason))

    # TODO: un-hard-code currencies
    @Plugin.on_message(r'.*(display|show).*cash pool.*')
    def show_pool(self, ch, _user, _groups):
        self.send(ch, "I've analyzed your cash pool.")
        with contextlib.closing(conn.cursor()) as cur:
            data = cur.execute(""" SELECT first_name,
                                          CAST(cad AS FLOAT) / 100,
                                          CAST(usd AS FLOAT) / 100
                                   FROM cash_pool
                                   INNER JOIN user
                                       ON user.uuid = cash_pool.uuid
                                   WHERE cad <> 0 OR usd <> 0
                                   ORDER BY first_name ASC
                               """).fetchall()

        for first_name, cad, usd in data:
            if cad:
                self.send(ch, '{} {} ${}{}'.format(
                    first_name.title(), 'owes' if cad > 0 else 'is owed',
                    abs(cad), ' CAD' if usd else ''))
            if usd:
                self.send(ch, '{} {} ${} USD'.format(
                    first_name.title(), 'owes' if usd > 0 else 'is owed',
                    abs(usd)))

        if not data:
            self.send(ch, 'All appears to be settled.')

    @Plugin.on_message(r'(.*) (\w+) (sent|paid) \$([\d\.]+) ?(|{}) '
                       r'(to|for) ([, \w]+)\.?'.format(
                           '|'.join(CURRENCIES).lower()))
    def send_cash(self, ch, user, groups):
        reason, single, _direction, value, currency, _, multiple = groups
        value = int(float(value) * 100)

        # TODO: user is not on slack
        with contextlib.closing(conn.cursor()) as cur:
            if single == 'i':
                s = user
            else:
                s = cur.execute(""" SELECT uuid
                                    FROM user
                                    WHERE first_name = ?
                                """, [single]).fetchone()[0]

            m = filter(lambda u: u != 'and', re.findall(DELIMITED, multiple))
            for idx, item in enumerate(m):
                if item == 'me':
                    m[idx] = user
                elif item in ('herself', 'himself'):
                    m[idx] = s
                else:
                    m[idx] = cur.execute(""" SELECT uuid
                                             FROM user
                                             WHERE first_name = ?
                                         """, [item]).fetchone()[0]

            if not currency:
                currency = DEFAULT_CURRENCY.lower()

            cur.execute(""" INSERT OR IGNORE INTO cash_pool (uuid)
                            VALUES (?)
                        """, [s])
            cur.execute(""" UPDATE cash_pool
                            SET {} = {} - ?
                            WHERE uuid = ?
                        """.format(currency, currency), [value, s])
            m_value = int(round(value / len(m)))
            for p in m:
                cur.execute(""" INSERT OR IGNORE INTO cash_pool (uuid)
                                VALUES (?)
                            """, [p])
                cur.execute(""" UPDATE cash_pool
                                SET {} = {} + ?
                                WHERE uuid = ?
                            """.format(currency, currency), [m_value, p])

            reason = reason[7:] if reason.startswith('jarvis') else reason
            cur.execute(""" INSERT INTO cash_pool_history (source, targets,
                                                           value, currency,
                                                           reason, created_by)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [s, str(m), value / 100., currency,
                              reason.strip(' ,.?!'), user])
            conn.commit()

        self.send(ch, 'Very good, sir.')

    @staticmethod
    def revert_user_change(user):
        with contextlib.closing(conn.cursor()) as cur:
            last = cur.execute(""" SELECT source, targets, value, currency
                                   FROM cash_pool_history
                                   WHERE created_by = ?
                                   ORDER BY created_at DESC
                                   LIMIT 1
                               """, [user]).fetchone()
        if not last:
            return False

        source, targets, value, currency = last
        target = eval(targets)  # pylint: disable=W0123

        with contextlib.closing(conn.cursor()) as cur:
            cur.execute(""" UPDATE cash_pool
                                SET {} = {} + ?
                                WHERE uuid = ?
                            """.format(currency, currency), [value, source])

            for target in targets:
                m_value = int(round(value / len(targets)))
                cur.execute(""" UPDATE cash_pool
                                SET {} = {} - ?
                                WHERE uuid = ?
                            """.format(currency, currency), [m_value, target])

            cur.execute(""" INSERT INTO cash_pool_history (source, targets,
                                                           value, currency,
                                                           reason, created_by)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, [source, str(targets), value / 100., currency,
                              'REVERT', user])
            conn.commit()

        return True

    @Plugin.on_message(r'.*revert my .*cash pool change.*')
    def revert_own_change(self, ch, user, _groups):
        if not self.revert_user_change(user):
            self.send(ch, 'I could not find a change to revert.')
            return

        self.send(ch, "Yes, sir; I've cleaned up your tomfoolery.")

    @Plugin.require_auth
    @Plugin.on_message(r'.*revert the .*cash pool change.*')
    def revert_any_change(self, ch, _user, _groups):
        with contextlib.closing(conn.cursor()) as cur:
            user = cur.execute(""" SELECT created_by
                                   FROM cash_pool_history
                                   ORDER BY created_at DESC
                                   LIMIT 1
                               """).fetchone()
        if not user:
            self.send(ch, 'It appears no one has used this feature yet.')
            return

        if not self.revert_user_change(user):
            self.send(ch, 'I could not find a change to revert.')
            return

        self.send(ch, "Yes, sir; I've cleaned up the tomfoolery.")

    @Plugin.on_message(r'.*currencies.*support(ed)?.*')
    def get_all_currencies(self, ch, _user, _groups):
        supported = CURRENCIES[:]
        if len(supported) > 2:
            for i in xrange(len(supported) - 1):
                supported[i] = supported[i] + ','

        supported.insert(-1, 'and')
        supported = ' '.join(supported)

        self.send(ch, 'I support {}.'.format(supported))

    @Plugin.on_message(r'.*default.*currency.*')
    def get_default_currency(self, ch, _user, _groups):
        self.send(ch, 'My default currency is {}.'.format(DEFAULT_CURRENCY))
