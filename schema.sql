-- Структура базы данных для WellnessBot (SQLite)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    username TEXT,
    reminder_time TEXT DEFAULT '20:00',
    reminder_enabled INTEGER DEFAULT 1,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    mood INTEGER,
    work_hours REAL,
    sleep_hours REAL,
    comment TEXT
);