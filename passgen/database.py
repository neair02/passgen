import sqlite3
import os
from flask import g

DATABASE = os.environ.get('DATABASE', 'passwords.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            label      TEXT    NOT NULL,
            login      TEXT    DEFAULT '',
            password   TEXT    NOT NULL,
            created_at DATETIME DEFAULT (datetime('now','localtime'))
        )
    """)
    db.commit()


def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
