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
    info            BLOB        NOT NULL,
    created_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);
"""
import sqlite3


conn = sqlite3.connect('jarvis.db')


def initialize_database():
    cur = conn.cursor()
    try:
        cur.executescript(__doc__)
    finally:
        cur.close()
