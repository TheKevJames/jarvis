import jarvis.db.dal as dal


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

        print(CashPoolDal.ensure, [source])
        cur.execute(CashPoolDal.ensure, [source])
        cur.execute(dec, [value, source])
        for target in targets:
            target_value = int(round(value / len(targets)))
            cur.execute(CashPoolDal.ensure, [target])
            cur.execute(inc, [target_value, target])


class CashPoolHistoryDal(dal.Dal):
    # pylint: disable=E0213
    columns = ['source', 'targets', 'value', 'currency', 'reason',
               'created_by', 'date']

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
