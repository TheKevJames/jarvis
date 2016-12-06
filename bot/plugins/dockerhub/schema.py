"""
DROP TABLE IF EXISTS dockerhub_repository;
CREATE TABLE dockerhub_repository (
    uuid            CHAR(16)    NOT NULL,
    repository      CHAR(64)    NOT NULL,
    PRIMARY KEY (uuid, repository),
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
DROP TABLE IF EXISTS dockerhub_username;
CREATE TABLE dockerhub_username (
    uuid            CHAR(16)    PRIMARY KEY,
    username        CHAR(64),
    FOREIGN KEY (uuid) REFERENCES user(uuid)
);
"""
import contextlib

from jarvis.db import connection


def initialize():
    with contextlib.closing(connection.cursor()) as cur:
        cur.executescript(__doc__)
