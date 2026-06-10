from datetime import date
from enum import Enum, auto

import database as db
import keyboards
import graph

class State(Enum):
    MOOD = auto()
    WORK = auto()
    SLEEP = auto()
    COMMENT = auto()
    WORK_CUSTOM = auto()
    SLEEP_CUSTOM = auto()

fsm = {}

def set_state(uid, state):
    fsm[uid] = {"state": state}

def get_state(uid):
    return fsm.get(uid, {}).get("state")

def set_data(uid, key, value):
    if uid not in fsm:
        fsm[uid] = {}
    fsm[uid][key] = value

def clear_state(uid):
    return fsm.pop(uid, {})

def send(bot, uid, text, kb=None):
    bot.send_message(uid, text, reply_markup=kb)

def to_float(text):
    try:
        return float(text.replace(",", "."))
    except:
        return None

def finish(bot, uid, comment=""):
    data = clear_state(uid)
    db.add_record(
        uid,
        date.today().isoformat(),
        data.get("mood"),
        data.get("work"),
        data.get("sleep"),
        comment
    )
    send(bot, uid, "✅ Сохранено!", keyboards.main())

def register_handlers(bot):

    @bot.message_handler(commands=["start", "help"])
    def start(msg):
        db.get_or_create_user(msg.chat.id, msg.from_user.username)
        send(bot, msg.chat.id, "👋 Добро пожаловать! Выбери действие:", keyboards.main())

    @bot.message_handler(func=lambda m: m.text == "👩‍💻 Помощь")
    def help_handler(msg):
        send(
            bot,
            msg.chat.id,
            "📖 *Команды:*\n"
            "/start - главное меню\n"
            "/help - помощь\n"
            "/add - записать день\n"
            "/stats - статистика\n"
            "/history - история\n"
            "/insights - инсайты\n"
            "/chart - график\n"
            "/reminder - настроить напоминание\n"
            "/clear - очистить данные\n\n"
            "Используй кнопки меню для быстрого доступа!",
            keyboards.main()
        )

    @bot.message_handler(commands=["add"])
    @bot.message_handler(func=lambda m: m.text == "➕ Записать день")
    def add(msg):
        uid = msg.chat.id
        if db.has_today_record(uid):
            return send(bot, uid, "⚠️ Запись на сегодня уже есть!", keyboards.main())
        set_state(uid, State.MOOD)
        send(bot, uid, "😊 *Шаг 1/4* — Какое у тебя настроение? (1-5)", keyboards.mood())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.MOOD)
    def mood(msg):
        uid = msg.chat.id
        if not msg.text or not msg.text[0].isdigit():
            return
        mood = int(msg.text[0])
        if mood not in range(1, 6):
            return
        set_data(uid, "mood", mood)
        set_state(uid, State.WORK)
        send(bot, uid, "💼 *Шаг 2/4* — Сколько часов работал/учился?", keyboards.work())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.WORK)
    def work(msg):
        uid = msg.chat.id
        if msg.text == "Другое":
            set_state(uid, State.WORK_CUSTOM)
            return send(bot, uid, "Введи количество часов (например: 3.5):")
        value = to_float(msg.text)
        if value is None or value < 0 or value > 24:
            return send(bot, uid, "❌ Введи число от 0 до 24")
        set_data(uid, "work", value)
        set_state(uid, State.SLEEP)
        send(bot, uid, "😴 *Шаг 3/4* — Сколько часов спал?", keyboards.sleep())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.WORK_CUSTOM)
    def work_custom(msg):
        uid = msg.chat.id
        value = to_float(msg.text)
        if value is None or value < 0 or value > 24:
            return send(bot, uid, "❌ Введи число от 0 до 24")
        set_data(uid, "work", value)
        set_state(uid, State.SLEEP)
        send(bot, uid, "😴 *Шаг 3/4* — Сколько часов спал?", keyboards.sleep())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.SLEEP)
    def sleep(msg):
        uid = msg.chat.id
        if msg.text == "Другое":
            set_state(uid, State.SLEEP_CUSTOM)
            return send(bot, uid, "Введи количество часов (например: 7.5):")
        value = to_float(msg.text)
        if value is None or value < 0 or value > 24:
            return send(bot, uid, "❌ Введи число от 0 до 24")
        set_data(uid, "sleep", value)
        set_state(uid, State.COMMENT)
        send(bot, uid, "💬 *Шаг 4/4* — Хочешь добавить комментарий?", keyboards.comment())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.SLEEP_CUSTOM)
    def sleep_custom(msg):
        uid = msg.chat.id
        value = to_float(msg.text)
        if value is None or value < 0 or value > 24:
            return send(bot, uid, "❌ Введи число от 0 до 24")
        set_data(uid, "sleep", value)
        set_state(uid, State.COMMENT)
        send(bot, uid, "💬 *Шаг 4/4* — Хочешь добавить комментарий?", keyboards.comment())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == State.COMMENT)
    def comment(msg):
        text = "" if msg.text == "Пропустить" else msg.text
        finish(bot, msg.chat.id, text)

    @bot.message_handler(commands=["stats"])
    @bot.message_handler(func=lambda m: m.text == "📊 Статистика")
    def stats(msg):
        uid = msg.chat.id
        recs = db.get_records(uid)

        if not recs:
            return send(bot, uid, "📭 Нет данных. Добавь первую запись через /add", keyboards.main())

        n = len(recs)
        text = (
            f"📊 *Статистика за {n} дней*\n\n"
            f"😊 Настроение: {sum(r['mood'] for r in recs)/n:.1f}/5\n"
            f"💼 Работа: {sum(r['work_hours'] for r in recs)/n:.1f} ч/день\n"
            f"😴 Сон: {sum(r['sleep_hours'] for r in recs)/n:.1f} ч/ночь"
        )
        send(bot, uid, text, keyboards.main())

    @bot.message_handler(commands=["history"])
    @bot.message_handler(func=lambda m: m.text == "📋 История")
    def history(msg):
        uid = msg.chat.id
        recs = db.get_records(uid)

        if not recs:
            return send(bot, uid, "📭 История пуста.", keyboards.main())

        text = "📜 *Последние 5 записей:*\n\n"
        for r in recs[-5:]:
            text += (
                f"📅 {r['date']}\n"
                f"  😊 {r['mood']}/5 | 💼 {r['work_hours']}ч | 😴 {r['sleep_hours']}ч\n"
                f"  💬 {r['comment'] if r['comment'] else '—'}\n\n"
            )
        send(bot, uid, text, keyboards.main())

    @bot.message_handler(commands=["insights"])
    @bot.message_handler(func=lambda m: m.text == "🔍 Мои инсайты")
    def insights(msg):
        uid = msg.chat.id
        recs = db.get_records(uid)
        text = graph.get_insights(recs) if recs else "📭 Недостаточно данных для анализа."
        send(bot, uid, text, keyboards.main())

    @bot.message_handler(commands=["chart"])
    @bot.message_handler(func=lambda m: m.text == "📉 График")
    def chart(msg):
        uid = msg.chat.id
        recs = db.get_records(uid)

        if len(recs) < 2:
            return send(bot, uid, "📭 Нужно минимум 2 записи для графика.", keyboards.main())

        filename = f"chart_{uid}.png"
        graph.create_chart(recs, filename)

        with open(filename, "rb") as file:
            bot.send_photo(uid, file, caption="📈 Динамика показателей")
        send(bot, uid, "Готово!", keyboards.main())

    @bot.message_handler(commands=["reminder"])
    @bot.message_handler(func=lambda m: m.text == "⏰ Напоминание")
    def reminder_settings(msg):
        uid = msg.chat.id
        rem = db.get_reminder(uid)
        status = "✅ вкл" if rem["reminder_enabled"] else "❌ выкл"
        set_state(uid, "reminder")
        send(bot, uid, f"⏰ *Напоминание*\n\nВремя: {rem['reminder_time']} ({status})\n\nВведи новое время (ЧЧ:ММ) или 'выкл':", keyboards.reminder())

    @bot.message_handler(func=lambda m: m.text == "⏰ Выключить")
    def reminder_off(msg):
        uid = msg.chat.id
        db.update_reminder(uid, "20:00", False)
        clear_state(uid)
        send(bot, uid, "🔕 Напоминания выключены.", keyboards.main())

    @bot.message_handler(func=lambda m: m.text == "⏰ Включить")
    def reminder_on(msg):
        uid = msg.chat.id
        rem = db.get_reminder(uid)
        db.update_reminder(uid, rem["reminder_time"], True)
        clear_state(uid)
        send(bot, uid, f"🔔 Напоминания включены на {rem['reminder_time']}.", keyboards.main())

    @bot.message_handler(func=lambda m: m.text == "Назад")
    def back(msg):
        clear_state(msg.chat.id)
        send(bot, msg.chat.id, "Главное меню:", keyboards.main())

    @bot.message_handler(func=lambda m: get_state(m.chat.id) == "reminder" and m.text and ":" in m.text)
    def reminder_time(msg):
        uid = msg.chat.id
        text = msg.text.strip()
        try:
            h, m = map(int, text.split(':'))
            if 0 <= h <= 23 and 0 <= m <= 59:
                db.update_reminder(uid, f"{h:02d}:{m:02d}", True)
                clear_state(uid)
                send(bot, uid, f"✅ Напоминание установлено на {h:02d}:{m:02d}", keyboards.main())
            else:
                send(bot, uid, "❌ Неверный формат. Пример: 21:30")
        except:
            send(bot, uid, "❌ Неверный формат. Пример: 21:30")

    @bot.message_handler(commands=["clear"])
    @bot.message_handler(func=lambda m: m.text == "🗑 Очистить данные")
    def clear(msg):
        send(bot, msg.chat.id, "⚠️ Удалить все записи?", keyboards.clear())

    @bot.message_handler(func=lambda m: m.text == "✅ Да, удалить")
    def clear_yes(msg):
        db.clear_data(msg.chat.id)
        send(bot, msg.chat.id, "🗑 Все записи удалены.", keyboards.main())

    @bot.message_handler(func=lambda m: m.text == "❌ Нет")
    def clear_no(msg):
        send(bot, msg.chat.id, "Отмена.", keyboards.main())

    @bot.message_handler(func=lambda m: True)
    def fallback(msg):
        if get_state(msg.chat.id):
            return
        send(bot, msg.chat.id, "Используй кнопки меню или /help", keyboards.main())