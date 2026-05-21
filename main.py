import logging
import os
from datetime import datetime

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from database import init_db, get_all_reminders
from handler import register_handlers

load_dotenv()

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в файле .env")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def _check_and_send_reminders():
    current_hm = datetime.now().strftime('%H:%M')
    try:
        for row in get_all_reminders():
            rt = str(row['reminder_time'])[:5]
            if rt == current_hm:
                try:
                    bot.send_message(
                        row['user_id'],
                        "⏰ Привет! Время записать свой день.\n"
                        "Нажми /add или кнопку ➕ *Записать день*",
                        parse_mode='Markdown',
                    )
                except Exception as e:
                    logger.warning("Не удалось отправить напоминание пользователю %s: %s", row['user_id'], e)
    except Exception as e:
        logger.error("Ошибка при проверке напоминаний: %s", e)


def _start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone='Europe/Moscow')
    scheduler.add_job(
        _check_and_send_reminders,
        CronTrigger(minute='*'),
        id='reminder_check',
        replace_existing=True,
    )
    scheduler.start()
    return scheduler


if __name__ == '__main__':
    init_db()
    register_handlers(bot)
    scheduler = _start_scheduler()
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    try:
        bot.infinity_polling(logger_level=logging.WARNING, timeout=30)
    finally:
        scheduler.shutdown()
        print("Бот остановлен.")
