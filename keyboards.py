from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("➕ Записать день"),
        KeyboardButton("📊 Статистика"),
        KeyboardButton("📋 История"),
        KeyboardButton("⚙️ Настройки"),
    )
    return kb


def mood_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=5)
    buttons = [
        InlineKeyboardButton("1 😞", callback_data="mood_1"),
        InlineKeyboardButton("2 😐", callback_data="mood_2"),
        InlineKeyboardButton("3 🙂", callback_data="mood_3"),
        InlineKeyboardButton("4 😊", callback_data="mood_4"),
        InlineKeyboardButton("5 🤩", callback_data="mood_5"),
    ]
    kb.add(*buttons)
    return kb


def work_hours_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=5)
    buttons = [
        InlineKeyboardButton("0.5 ч", callback_data="work_0.5"),
        InlineKeyboardButton("1 ч",   callback_data="work_1"),
        InlineKeyboardButton("2 ч",   callback_data="work_2"),
        InlineKeyboardButton("4 ч",   callback_data="work_4"),
        InlineKeyboardButton("Другое…", callback_data="work_custom"),
    ]
    kb.add(*buttons)
    return kb


def sleep_hours_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=5)
    buttons = [
        InlineKeyboardButton("6 ч", callback_data="sleep_6"),
        InlineKeyboardButton("7 ч", callback_data="sleep_7"),
        InlineKeyboardButton("8 ч", callback_data="sleep_8"),
        InlineKeyboardButton("9 ч", callback_data="sleep_9"),
        InlineKeyboardButton("Другое…", callback_data="sleep_custom"),
    ]
    kb.add(*buttons)
    return kb


def skip_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Пропустить ➡️", callback_data="skip_comment"))
    return kb


def stats_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📅 За неделю",      callback_data="stats_week"),
        InlineKeyboardButton("🗓 За месяц",        callback_data="stats_month"),
        InlineKeyboardButton("🔍 Мои инсайты",    callback_data="stats_insights"),
        InlineKeyboardButton("📉 График",          callback_data="stats_graph"),
    )
    return kb


def graph_period_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📅 7 дней",  callback_data="graph_week"),
        InlineKeyboardButton("🗓 30 дней", callback_data="graph_month"),
    )
    return kb


def confirm_clear_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Да, удалить", callback_data="confirm_clear"),
        InlineKeyboardButton("❌ Отмена",      callback_data="cancel_clear"),
    )
    return kb
