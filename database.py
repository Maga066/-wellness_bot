import os
from datetime import date, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_DB_CONFIG = {
    'host':     os.getenv('DB_HOST'),
    'port':     int(os.getenv('DB_PORT')),
    'dbname':   os.getenv('DB_NAME'),
    'user':     os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
}


def _conn():
    return psycopg2.connect(**_DB_CONFIG)


def init_db():
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id          BIGINT  PRIMARY KEY,
                    username         VARCHAR(255),
                    reminder_time    TIME    DEFAULT '20:00',
                    reminder_enabled BOOLEAN DEFAULT TRUE,
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS entries (
                    id          SERIAL   PRIMARY KEY,
                    user_id     BIGINT   NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    entry_date  DATE     NOT NULL DEFAULT CURRENT_DATE,
                    mood        SMALLINT NOT NULL CHECK (mood BETWEEN 1 AND 5),
                    work_hours  NUMERIC(4, 1) NOT NULL CHECK (work_hours >= 0 AND work_hours <= 24),
                    sleep_hours NUMERIC(4, 1) NOT NULL CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
                    comment     TEXT,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (user_id, entry_date)
                );

                CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries (user_id, entry_date);
            """)
        conn.commit()


def get_or_create_user(user_id: int, username: str = None):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, username)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
            """, (user_id, username))
        conn.commit()


def get_reminder(user_id: int) -> dict | None:
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT reminder_time, reminder_enabled FROM users WHERE user_id = %s",
                (user_id,)
            )
            return cur.fetchone()


def update_reminder(user_id: int, time_str: str, enabled: bool = True):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET reminder_time = %s, reminder_enabled = %s WHERE user_id = %s",
                (time_str, enabled, user_id)
            )
        conn.commit()


def get_all_reminders() -> list:
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT user_id, reminder_time
                FROM users
                WHERE reminder_enabled = TRUE AND reminder_time IS NOT NULL
            """)
            return cur.fetchall()


def add_entry(user_id: int, mood: int, work_hours: float,
              sleep_hours: float, comment: str = None):
    today = date.today()
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO entries (user_id, entry_date, mood, work_hours, sleep_hours, comment)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, entry_date) DO UPDATE SET
                    mood        = EXCLUDED.mood,
                    work_hours  = EXCLUDED.work_hours,
                    sleep_hours = EXCLUDED.sleep_hours,
                    comment     = EXCLUDED.comment,
                    created_at  = CURRENT_TIMESTAMP
            """, (user_id, today, mood, work_hours, sleep_hours, comment))
        conn.commit()


def get_entries(user_id: int, days: int = 7) -> list:
    since = date.today() - timedelta(days=days - 1)
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT entry_date, mood, work_hours, sleep_hours, comment
                FROM entries
                WHERE user_id = %s AND entry_date >= %s
                ORDER BY entry_date
            """, (user_id, since))
            return cur.fetchall()


def get_history(user_id: int, limit: int = 10) -> list:
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT entry_date, mood, work_hours, sleep_hours, comment
                FROM entries
                WHERE user_id = %s
                ORDER BY entry_date DESC
                LIMIT %s
            """, (user_id, limit))
            return cur.fetchall()


def get_stats_summary(user_id: int, days: int) -> dict | None:
    since = date.today() - timedelta(days=days - 1)
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(*)                   AS total_days,
                    ROUND(AVG(mood), 2)        AS avg_mood,
                    ROUND(AVG(work_hours), 2)  AS avg_work,
                    ROUND(AVG(sleep_hours), 2) AS avg_sleep,
                    MAX(mood)                  AS max_mood,
                    MIN(mood)                  AS min_mood,
                    MAX(work_hours)            AS max_work,
                    MAX(sleep_hours)           AS max_sleep
                FROM entries
                WHERE user_id = %s AND entry_date >= %s
            """, (user_id, since))
            return cur.fetchone()


def get_insights(user_id: int) -> dict:
    with _conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:

            cur.execute("""
                SELECT
                    TO_CHAR(entry_date, 'Day') AS dow,
                    ROUND(AVG(mood), 2)        AS avg_mood,
                    COUNT(*)                   AS cnt
                FROM entries
                WHERE user_id = %s
                GROUP BY EXTRACT(DOW FROM entry_date), TO_CHAR(entry_date, 'Day')
                ORDER BY avg_mood DESC
                LIMIT 1
            """, (user_id,))
            best_day = cur.fetchone()

            cur.execute("""
                SELECT
                    CASE
                        WHEN sleep_hours < 6 THEN 'мало (<6ч)'
                        WHEN sleep_hours < 7 THEN '6–7ч'
                        WHEN sleep_hours < 8 THEN '7–8ч'
                        ELSE 'много (8+ч)'
                    END                        AS sleep_bucket,
                    ROUND(AVG(mood), 2)        AS avg_mood,
                    COUNT(*)                   AS cnt
                FROM entries
                WHERE user_id = %s
                GROUP BY sleep_bucket
                ORDER BY avg_mood DESC
            """, (user_id,))
            sleep_mood = cur.fetchall()

            cur.execute("""
                SELECT
                    CASE
                        WHEN work_hours <= 2 THEN 'мало (≤2ч)'
                        WHEN work_hours <= 5 THEN 'средне (2–5ч)'
                        ELSE 'много (>5ч)'
                    END                        AS work_bucket,
                    ROUND(AVG(mood), 2)        AS avg_mood,
                    COUNT(*)                   AS cnt
                FROM entries
                WHERE user_id = %s
                GROUP BY work_bucket
                ORDER BY avg_mood DESC
            """, (user_id,))
            work_mood = cur.fetchall()

            cur.execute("""
                SELECT entry_date, mood, work_hours, sleep_hours
                FROM entries
                WHERE user_id = %s
                ORDER BY mood DESC, sleep_hours DESC
                LIMIT 1
            """, (user_id,))
            best_entry = cur.fetchone()

            cur.execute("""
                SELECT entry_date, mood, work_hours, sleep_hours
                FROM entries
                WHERE user_id = %s
                ORDER BY mood ASC, sleep_hours ASC
                LIMIT 1
            """, (user_id,))
            worst_entry = cur.fetchone()

            return {
                'best_day':    best_day,
                'sleep_mood':  sleep_mood,
                'work_mood':   work_mood,
                'best_entry':  best_entry,
                'worst_entry': worst_entry,
            }


def delete_user_data(user_id: int):
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM entries WHERE user_id = %s", (user_id,))
        conn.commit()
