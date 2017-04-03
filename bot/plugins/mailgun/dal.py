import sqlite3

import jarvis.db.dal as dal


class MailgunDal(dal.Dal):
    def create_domain(cur, uuid, domain):
        try:
            cur.execute(""" INSERT INTO mailgun_domain (uuid, domain)
                            VALUES (?, ?)
                        """, [uuid, domain])
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_domain(cur, uuid, domain):
        cur.execute(""" DELETE FROM mailgun_domain
                        WHERE uuid = ?
                        AND domain = ?
                    """, [uuid, domain])

    def read_by_domain(cur, domain):
        return cur.execute(""" SELECT uuid
                               FROM mailgun_domain
                               WHERE domain = ?
                           """, [domain]).fetchone()
