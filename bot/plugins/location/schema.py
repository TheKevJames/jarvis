"""
DROP TABLE IF EXISTS user_data;
CREATE TABLE user_data (
    uuid            CHAR(16)    PRIMARY KEY,
    place           CHAR(64),
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
"""
import contextlib

from jarvis.db import connection


def initialize():
    with contextlib.closing(connection.cursor()) as cur:
        cur.executescript(__doc__)
