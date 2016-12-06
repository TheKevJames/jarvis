"""
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
