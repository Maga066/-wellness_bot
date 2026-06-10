import logging
import os
import threading
import time
from datetime import datetime

import telebot
from dotenv import load_dotenv

import database as db
from handler import register_handlers

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в файле .env")

bot = telebot.TeleBot(BOT_TOKEN)

reminder_thread = None
stop_reminder = False


def check_reminders():
    while not stop_reminder:
        now = datetime.now().strftime('%H:%M')
        users = db.get_all_users_with_reminder()
        for user in users:
            if user['reminder_time'] == now:
                try:
                    bot.send_message(
                        user['telegram_id'],
                        "⏰ *Напоминание!*\n\nНе забудь записать свой день: /add",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Ошибка отправки {user['telegram_id']}: {e}")
        time.sleep(60)


def start_scheduler():
    global reminder_thread, stop_reminder
    stop_reminder = False
    reminder_thread = threading.Thread(target=check_reminders, daemon=True)
    reminder_thread.start()


if __name__ == '__main__':
    db.init_db()
    db.load_test_data()
    register_handlers(bot)
    start_scheduler()
    print("🤖 Бот запущен. Нажмите Ctrl+C для остановки.")
    try:
        bot.infinity_polling(timeout=30)
    except KeyboardInterrupt:
        stop_reminder = True
        print("🤖 Бот остановлен.")