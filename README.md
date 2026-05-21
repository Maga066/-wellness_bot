# WellnessBot 🤖

Telegram-бот для ежедневного отслеживания самочувствия и продуктивности. Собирает данные о настроении, сне и работе, хранит их в PostgreSQL и выявляет скрытые закономерности с помощью аналитики и графиков.

---

## Структура проекта

```
.
├── main.py          # Точка входа: инициализация бота, планировщик, polling
├── handler.py       # Все обработчики команд и колбэков (роуты)
├── keyboards.py     # Все клавиатуры (ReplyKeyboard и InlineKeyboard)
├── database.py      # Подключение к БД и все SQL-методы
├── graph.py         # Генерация графиков через matplotlib
├── schema.sql       # DDL: создание таблиц и индексов
├── test_data.sql    # Тестовые данные (15 записей)
├── requirements.txt # Зависимости с версиями
├── .env.example     # Пример файла переменных окружения
└── .gitignore
```

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <URL репозитория>
cd <папка проекта>
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Настроить переменные окружения

Скопировать `.env.example` в `.env` и заполнить:

```
BOT_TOKEN=токен_от_BotFather
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wellness_bot
DB_USER=postgres
DB_PASSWORD=ваш_пароль
```

### 4. Создать базу данных PostgreSQL

```sql
CREATE DATABASE wellness_bot;
```

Затем применить схему:

```bash
psql -U postgres -d wellness_bot -f schema.sql
```

*(опционально)* Загрузить тестовые данные:

```bash
psql -U postgres -d wellness_bot -f test_data.sql
```

### 5. Запустить бота

```bash
python main.py
```

---

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и инструкция |
| `/add` | Записать данные за сегодня |
| `/stats` | Статистика (неделя / месяц / инсайты / график) |
| `/history` | Последние 10 записей |
| `/settings` | Изменить время напоминания |
| `/clear` | Удалить все свои данные |
| `/help` | Справка |

Также доступны кнопки главного меню: **➕ Записать день**, **📊 Статистика**, **📋 История**, **⚙️ Настройки**.

---

## Технологии

- **Python 3.11+**
- **pyTelegramBotAPI** — Telegram Bot API
- **psycopg2** — PostgreSQL драйвер
- **APScheduler** — планировщик напоминаний
- **matplotlib** — графики
- **python-dotenv** — переменные окружения
