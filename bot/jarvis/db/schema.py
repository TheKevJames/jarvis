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
"""
import contextlib

from jarvis.db import connection


def initialize():
    with contextlib.closing(connection.cursor()) as cur:
        cur.executescript(__doc__)
