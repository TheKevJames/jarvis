"""
DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,
    uuid            CHAR(16)    UNIQUE NOT NULL,
    channel         CHAR(16)    NOT NULL,
    first_name      CHAR(64)    NOT NULL,
    last_name       CHAR(64),
    email           CHAR(128)   NOT NULL,
    username        CHAR(32)    NOT NULL,
    is_admin        INTEGER     NOT NULL DEFAULT 0
);
DROP TABLE IF EXISTS user_data;
CREATE TABLE user_data (
    uuid            CHAR(16)    PRIMARY KEY,
    place           CHAR(64),
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
DROP TABLE IF EXISTS cash_pool;
CREATE TABLE cash_pool (
    uuid            CHAR(16)    PRIMARY KEY,
    cad             INTEGER     DEFAULT 0,
    usd             INTEGER     DEFAULT 0,
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
DROP TABLE IF EXISTS cash_pool_history;
CREATE TABLE cash_pool_history (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,
    source          CHAR(16)    NOT NULL,
    targets         BLOB        NOT NULL,
    value           REAL        NOT NULL,
    currency        CHAR(8)     NOT NULL,
    reason          CHAR(512),
    created_by      CHAR(16)    NOT NULL,
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES user(uuid),
    FOREIGN KEY (source) REFERENCES user(uuid)
);
"""
import contextlib
import sqlite3


from jarvis.core.helper import get_user_fields


conn = sqlite3.connect('jarvis.db')


def initialize_database():
    with contextlib.closing(conn.cursor()) as cur:
        cur.executescript(__doc__)


def create_user(slack, user):
    with contextlib.closing(conn.cursor()) as cur:
        cur.execute(""" INSERT INTO user
                        (uuid, first_name, last_name, email, username,
                         is_admin, channel)
                        VALUES (?, ?, ?, ?, ?, ?, ?) """,
                    get_user_fields(slack, user))
        conn.commit()


def get_admin_channels():
    with contextlib.closing(conn.cursor()) as cur:
        for user in cur.execute(""" SELECT channel
                                        FROM user
                                        WHERE is_admin = 1
                                    """).fetchall():
            if user[0]:
                yield user[0]


def is_admin(uuid):
    with contextlib.closing(conn.cursor()) as cur:
        admin = cur.execute(""" SELECT is_admin
                                FROM user
                                WHERE uuid = ?
                            """, [uuid]).fetchone()

    return admin[0]


def is_direct_channel(channel):
    with contextlib.closing(conn.cursor()) as cur:
        return cur.execute(""" SELECT 1 FROM user WHERE channel = ? """,
                           [channel]).fetchone()


def update_user(slack, user):
    with contextlib.closing(conn.cursor()) as cur:
        cur.execute(""" INSERT OR REPLACE INTO user
                        (uuid, first_name, last_name, email, username,
                         is_admin, channel)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, get_user_fields(slack, user))
        conn.commit()
