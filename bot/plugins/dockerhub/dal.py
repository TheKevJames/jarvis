import jarvis.db.dal as dal


class DockerhubDal(dal.Dal):
    # pylint: disable=E0213
    def read_by_repository(cur, repository):
        return cur.execute(""" SELECT uuid
                               FROM dockerhub_repository
                               WERE repository = ? """,
                           [repository]).fetchone()

    def read_by_username(cur, username):
        return cur.execute(""" SELECT uuid
                               FROM dockerhub_username
                               WHERE username = ? """,
                           [username]).fetchone()
