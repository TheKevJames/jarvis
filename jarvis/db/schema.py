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

from jarvis.db import connection


def initialize():
    with contextlib.closing(connection.cursor()) as cur:
        cur.executescript(__doc__)
