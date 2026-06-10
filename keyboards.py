from telebot import types

def main():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Записать день", "📊 Статистика")
    kb.add("📋 История", "📉 График")
    kb.add("🔍 Мои инсайты", "⏰ Напоминание")
    kb.add("🗑 Очистить данные", "👩‍💻 Помощь")
    return kb

def mood():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("1 😞", "2 😐", "3 🙂", "4 😊", "5 🤩")
    return kb

def work():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("1", "2", "4", "6", "8")
    kb.add("Другое")
    return kb

def sleep():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("6", "7", "8", "9", "10")
    kb.add("Другое")
    return kb

def comment():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Пропустить")
    return kb

def reminder():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⏰ Выключить", "⏰ Включить")
    kb.add("Назад")
    return kb

def clear():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Да, удалить", "❌ Нет")
    return kb