import jarvis.db.dal as dal


class UsersDal(dal.Dal):
    # pylint: disable=E0213
    def create(cur, uuid, first_name, last_name, email, username, is_admin,
               channel):
        cur.execute(""" INSERT INTO user
                            (uuid, first_name, last_name, email, username,
                             is_admin, channel)
                        VALUES (?, ?, ?, ?, ?, ?, ?) """,
                    [uuid, first_name, last_name, email, username, is_admin,
                     channel])

    def is_admin(cur, uuid):
        return cur.execute(""" SELECT is_admin FROM user WHERE uuid = ? """,
                           [uuid]).fetchone()[0]

    def read_lookup_table(cur):
        return {k: v for k, v in cur.execute(
            """ SELECT uuid, first_name FROM user """).fetchall()}

    def read_by_name(cur, name):
        return cur.execute(""" SELECT uuid FROM user WHERE first_name = ? """,
                           [name]).fetchone()[0]

    def update(cur, uuid, first_name, last_name, email, username, is_admin,
               channel):
        cur.execute(""" UPDATE user
                        SET first_name = ?, last_name = ?, email = ?,
                            username = ?, is_admin = ?, channel = ?
                        WHERE uuid = ? """,
                    [first_name, last_name, email, username, is_admin,
                     channel, uuid])
