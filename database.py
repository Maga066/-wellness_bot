import sqlite3
from datetime import date, timedelta

DB_NAME = "8108522195"


def connect():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                mood INTEGER,
                work_hours REAL,
                sleep_hours REAL,
                comment TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                reminder_time TEXT DEFAULT '20:00',
                reminder_enabled INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        conn.commit()


def get_or_create_user(telegram_id: int, username: str = None):
    with connect() as conn:
        cursor = conn.execute(
            "SELECT telegram_id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        if not cursor.fetchone():
            conn.execute(
                "INSERT INTO users (telegram_id, username, created_at) VALUES (?, ?, ?)",
                (telegram_id, username, date.today().isoformat())
            )
            conn.commit()


def add_record(uid, day, mood, work, sleep, comment):
    with connect() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO records (user_id, date, mood, work_hours, sleep_hours, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (uid, day, mood, work, sleep, comment))
        conn.commit()


def has_today_record(uid):
    today = date.today().isoformat()
    with connect() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM records WHERE user_id = ? AND date = ?",
            (uid, today)
        )
        return cursor.fetchone()[0] > 0


def get_records(uid, days=None):
    with connect() as conn:
        if days:
            since = (date.today() - timedelta(days=days - 1)).isoformat()
            cursor = conn.execute("""
                SELECT * FROM records
                WHERE user_id = ? AND date >= ?
                ORDER BY date
            """, (uid, since))
        else:
            cursor = conn.execute(
                "SELECT * FROM records WHERE user_id = ? ORDER BY date",
                (uid,)
            )
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def clear_data(uid):
    with connect() as conn:
        conn.execute("DELETE FROM records WHERE user_id = ?", (uid,))
        conn.commit()


def get_reminder(telegram_id: int):
    with connect() as conn:
        cursor = conn.execute(
            "SELECT reminder_time, reminder_enabled FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = cursor.fetchone()
        if row:
            return {"reminder_time": row[0], "reminder_enabled": bool(row[1])}
        return {"reminder_time": "20:00", "reminder_enabled": True}


def update_reminder(telegram_id: int, time_str: str, enabled: bool = True):
    with connect() as conn:
        conn.execute(
            "UPDATE users SET reminder_time = ?, reminder_enabled = ? WHERE telegram_id = ?",
            (time_str, 1 if enabled else 0, telegram_id)
        )
        conn.commit()


def get_all_users_with_reminder():
    with connect() as conn:
        cursor = conn.execute("""
            SELECT telegram_id, reminder_time
            FROM users
            WHERE reminder_enabled = 1 AND reminder_time IS NOT NULL
        """)
        return [{"telegram_id": row[0], "reminder_time": row[1]} for row in cursor.fetchall()]


def load_test_data():
    with connect() as conn:
        with open("test_data.sql", "r", encoding="utf-8") as file:
            conn.executescript(file.read())
        conn.commit()