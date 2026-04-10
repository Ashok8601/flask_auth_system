import sqlite3
import sqlite3

def db_init():
    conn = sqlite3.connect('instaclone.db')
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT UNIQUE
    )
    """)

    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('instaclone.db')
    conn.row_factory = sqlite3.Row
    return conn   # 🔥 MOST IMPORTANT