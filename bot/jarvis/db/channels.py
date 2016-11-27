import jarvis.db.dal as dal


class ChannelsDal(dal.Dal):
    # pylint: disable=E0213
    def is_direct(cur, channel):
        return cur.execute('SELECT 1 FROM user WHERE channel = ?',
                           [channel]).fetchone()

    def read(cur, admin_only=False):
        users = []
        for u in cur.execute('SELECT channel, is_admin FROM user').fetchall():
            if admin_only and not u[1]:
                continue

            users.append(u[0])

        return users
