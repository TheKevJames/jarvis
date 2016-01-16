"""
CREATE TABLE user (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,
    uuid            CHAR(16),
    channel         CHAR(16),
    first_name      CHAR(64),
    last_name       CHAR(64),
    is_admin        INTEGER     NOT NULL DEFAULT 0
);
CREATE TABLE user_data (
    uuid            CHAR(16)    PRIMARY KEY,
    place           CHAR(64),
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
CREATE TABLE cash_pool (
    uuid            CHAR(16)    PRIMARY KEY,
    cad             INTEGER     DEFAULT 0,
    usd             INTEGER     DEFAULT 0,
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
CREATE TABLE cash_pool_history (
    id              INTEGER     PRIMARY KEY AUTOINCREMENT,
    source          CHAR(16)    NOT NULL,
    targets         BLOB        NOT NULL,
    value           REAL        NOT NULL,
    reason          CHAR(512),
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source) REFERENCES user(uuid)
);
"""
import contextlib
import sqlite3


conn = sqlite3.connect('jarvis.db')


def initialize_database():
    with contextlib.closing(conn.cursor()) as cur:
        cur.executescript(__doc__)


def is_admin(uuid):
    with contextlib.closing(conn.cursor()) as cur:
        admin = cur.execute(""" SELECT is_admin
                                FROM user
                                WHERE uuid = ?
                            """, [uuid]).fetchone()

    return admin[0]
