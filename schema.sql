-- schema.sql
-- Структура базы данных для WellnessBot

-- Таблица пользователей (настройки, время напоминания)
CREATE TABLE IF NOT EXISTS users (
    user_id          BIGINT PRIMARY KEY,
    username         VARCHAR(255),
    reminder_time    TIME    DEFAULT '20:00',
    reminder_enabled BOOLEAN DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица ежедневных записей
CREATE TABLE IF NOT EXISTS entries (
    id           SERIAL  PRIMARY KEY,
    user_id      BIGINT  NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    entry_date   DATE    NOT NULL DEFAULT CURRENT_DATE,
    mood         SMALLINT NOT NULL CHECK (mood BETWEEN 1 AND 5),
    work_hours   NUMERIC(4, 1) NOT NULL CHECK (work_hours >= 0 AND work_hours <= 24),
    sleep_hours  NUMERIC(4, 1) NOT NULL CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    comment      TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, entry_date)
);

-- Индекс для быстрой выборки по пользователю и дате
CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries (user_id, entry_date);
