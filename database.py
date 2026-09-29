import sqlite3
from pathlib import Path

# DB_PATH = Path(__file__).with_name("../repos/library.db")
DB_PATH = "../repos/library.db"

def get_connection():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_no TEXT UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            join_date TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT,
            title TEXT NOT NULL,
            author TEXT,
            publisher TEXT,
            year INTEGER,
            category TEXT,
            copies INTEGER NOT NULL DEFAULT 1,
            available_copies INTEGER NOT NULL DEFAULT 1,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            loan_date TEXT NOT NULL,
            due_date TEXT,
            return_date TEXT,
            status TEXT NOT NULL DEFAULT 'borrowed',
            notes TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            reservation_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'waiting',
            notes TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        book_columns = {row[1] for row in conn.execute("PRAGMA table_info(books)")}
        if "summary" not in book_columns:
            conn.execute("ALTER TABLE books ADD COLUMN summary TEXT")

def execute(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params)

def fetchall(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()

def fetchone(sql, params=()):
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()
