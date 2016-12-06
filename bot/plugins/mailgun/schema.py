"""
DROP TABLE IF EXISTS mailgun_domain;
CREATE TABLE mailgun_domain (
    uuid            CHAR(16)    NOT NULL,
    domain          CHAR(64)    NOT NULL,
    PRIMARY KEY (uuid, domain),
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
"""
import contextlib

from jarvis.db import connection


def initialize():
    with contextlib.closing(connection.cursor()) as cur:
        cur.executescript(__doc__)
