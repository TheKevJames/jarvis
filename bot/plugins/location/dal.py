import jarvis.db.dal as dal


class LocationDal(dal.Dal):
    # pylint: disable=E0213
    default_location = 'waterloo'

    def read(cur, uuid):
        loc = cur.execute(""" SELECT place FROM user_data WHERE uuid = ? """,
                          [uuid]).fetchone()
        return loc[0] if loc else LocationDal.default_location

    def update(cur, uuid, place):
        cur.execute(""" INSERT OR REPLACE INTO user_data (uuid, place)
                        VALUES (?, ?)""", [uuid, place])
