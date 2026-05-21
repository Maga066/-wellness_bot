import re
from datetime import date

import telebot
from telebot.types import Message, CallbackQuery

from database import (
    get_or_create_user,
    add_entry,
    get_entries,
    get_stats_summary,
    get_insights,
    get_history,
    update_reminder,
    get_reminder,
    delete_user_data,
)
from keyboards import (
    main_menu,
    mood_keyboard,
    work_hours_keyboard,
    sleep_hours_keyboard,
    skip_keyboard,
    stats_menu_keyboard,
    graph_period_keyboard,
    confirm_clear_keyboard,
)
from graph import generate_stats_graph

_IDLE         = 'idle'
_WORK_CUSTOM  = 'work_custom'
_SLEEP_CUSTOM = 'sleep_custom'
_COMMENT      = 'comment'
_REMINDER     = 'reminder'

_states: dict[int, str] = {}
_data:   dict[int, dict] = {}

MOOD_EMOJI = {1: '😞', 2: '😐', 3: '🙂', 4: '😊', 5: '🤩'}

DOW_RU = {
    'Monday':    'Понедельник',
    'Tuesday':   'Вторник',
    'Wednesday': 'Среда',
    'Thursday':  'Четверг',
    'Friday':    'Пятница',
    'Saturday':  'Суббота',
    'Sunday':    'Воскресенье',
}



def _state(uid: int) -> str:
    return _states.get(uid, _IDLE)


def _set_state(uid: int, state: str):
    _states[uid] = state


def _udata(uid: int) -> dict:
    return _data.setdefault(uid, {})


def _reset(uid: int):
    _states.pop(uid, None)
    _data.pop(uid, None)



def _save_entry(bot: telebot.TeleBot, uid: int, chat_id: int, comment: str | None):
    d = _udata(uid)
    mood  = d.get('mood')
    work  = d.get('work_hours')
    sleep = d.get('sleep_hours')

    if mood is None or work is None or sleep is None:
        bot.send_message(
            chat_id,
            "⚠️ Что-то пошло не так. Начни заново: /add",
            reply_markup=main_menu(),
        )
        _reset(uid)
        return

    add_entry(uid, mood, work, sleep, comment)
    _reset(uid)

    emoji = MOOD_EMOJI.get(mood, '🙂')
    comment_line = f"\n💬 _{comment}_" if comment else ''

    bot.send_message(
        chat_id,
        f"✅ *Запись сохранена!*\n\n"
        f"📅 {date.today().strftime('%d.%m.%Y')}\n"
        f"😊 Настроение: {emoji} {mood}/5\n"
        f"💼 Работа/учёба: {work} ч\n"
        f"😴 Сон: {sleep} ч"
        f"{comment_line}\n\n"
        f"Отличная работа! Продолжай отслеживать свой прогресс. 🌟",
        parse_mode='Markdown',
        reply_markup=main_menu(),
    )


def _show_stats(bot: telebot.TeleBot, uid: int, chat_id: int, days: int, label: str):
    stats = get_stats_summary(uid, days)

    if not stats or not stats['total_days']:
        period = 'последнюю неделю' if days == 7 else 'последние 30 дней'
        bot.send_message(
            chat_id,
            f"📭 За {period} нет данных.\nДобавь первую запись: /add",
            reply_markup=main_menu(),
        )
        return

    avg_mood_val = float(stats['avg_mood'])
    emoji = MOOD_EMOJI.get(round(avg_mood_val), '🙂')
    period = 'последнюю неделю' if days == 7 else 'последние 30 дней'

    text = (
        f"📊 *Статистика за {period}*\n\n"
        f"📝 Записей: *{stats['total_days']}*\n\n"
        f"😊 *Настроение*\n"
        f"  Среднее: {emoji} {stats['avg_mood']}/5\n"
        f"  Лучший день: {MOOD_EMOJI.get(stats['max_mood'], '🤩')} {stats['max_mood']}/5\n"
        f"  Худший день: {MOOD_EMOJI.get(stats['min_mood'], '😞')} {stats['min_mood']}/5\n\n"
        f"💼 *Работа/учёба*\n"
        f"  В среднем: {stats['avg_work']} ч/день\n"
        f"  Максимум: {stats['max_work']} ч\n\n"
        f"😴 *Сон*\n"
        f"  В среднем: {stats['avg_sleep']} ч/ночь\n"
        f"  Максимум: {stats['max_sleep']} ч"
    )
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=main_menu())


def _show_insights(bot: telebot.TeleBot, uid: int, chat_id: int):
    ins = get_insights(uid)
    lines = ["🔍 *Мои инсайты*\n"]

    if ins['best_day']:
        bd = ins['best_day']
        dow_en = bd['dow'].strip()
        dow_ru = DOW_RU.get(dow_en, dow_en)
        lines.append(
            f"📅 *Лучший день недели:* {dow_ru} "
            f"(среднее настроение: {bd['avg_mood']}/5, {bd['cnt']} зап.)\n"
        )

    if ins['sleep_mood']:
        lines.append("😴 *Влияние сна на настроение:*")
        for row in ins['sleep_mood']:
            e = MOOD_EMOJI.get(round(float(row['avg_mood'])), '🙂')
            lines.append(
                f"  • Сон {row['sleep_bucket']}: {e} {row['avg_mood']}/5 ({row['cnt']} дн.)"
            )
        lines.append('')

    if ins['work_mood']:
        lines.append("💼 *Влияние работы на настроение:*")
        for row in ins['work_mood']:
            e = MOOD_EMOJI.get(round(float(row['avg_mood'])), '🙂')
            lines.append(
                f"  • Работа {row['work_bucket']}: {e} {row['avg_mood']}/5 ({row['cnt']} дн.)"
            )
        lines.append('')

    if ins['best_entry']:
        be = ins['best_entry']
        lines.append(
            f"🌟 *Лучший день:* {be['entry_date'].strftime('%d.%m.%Y')} — "
            f"настроение {MOOD_EMOJI.get(be['mood'], '')} {be['mood']}/5, "
            f"сон {be['sleep_hours']}ч"
        )

    if ins['worst_entry']:
        we = ins['worst_entry']
        lines.append(
            f"😔 *Худший день:* {we['entry_date'].strftime('%d.%m.%Y')} — "
            f"настроение {MOOD_EMOJI.get(we['mood'], '')} {we['mood']}/5, "
            f"сон {we['sleep_hours']}ч"
        )

    if len(lines) == 1:
        bot.send_message(
            chat_id,
            "📭 Недостаточно данных для инсайтов. Добавь больше записей: /add",
            reply_markup=main_menu(),
        )
        return

    bot.send_message(chat_id, '\n'.join(lines), parse_mode='Markdown', reply_markup=main_menu())


def _send_graph(bot: telebot.TeleBot, uid: int, chat_id: int, days: int, label: str):
    entries = get_entries(uid, days)
    if not entries:
        bot.send_message(
            chat_id,
            f"📭 Нет данных за {label}. Добавь записи: /add",
            reply_markup=main_menu(),
        )
        return

    buf = generate_stats_graph(entries, title=f"Статистика за {label}")
    if buf:
        bot.send_photo(chat_id, buf, caption=f"📉 График за {label}", reply_markup=main_menu())
    else:
        bot.send_message(chat_id, "⚠️ Не удалось сгенерировать график.", reply_markup=main_menu())



def register_handlers(bot: telebot.TeleBot):

    @bot.message_handler(commands=['start'])
    def cmd_start(msg: Message):
        get_or_create_user(msg.from_user.id, msg.from_user.username)
        _reset(msg.from_user.id)
        bot.send_message(
            msg.chat.id,
            "👋 Привет! Я *WellnessBot* — твой личный дневник самочувствия.\n\n"
            "Я помогу тебе:\n"
            "• 📝 Ежедневно отслеживать настроение, сон и продуктивность\n"
            "• 📊 Видеть статистику и тренды\n"
            "• 🔍 Находить скрытые закономерности\n\n"
            "*Команды:*\n"
            "/add — Записать сегодняшний день\n"
            "/stats — Посмотреть статистику\n"
            "/history — История записей\n"
            "/settings — Настройки напоминаний\n"
            "/clear — Удалить все данные\n"
            "/help — Справка\n\n"
            "Начни с кнопки ➕ *Записать день*!",
            parse_mode='Markdown',
            reply_markup=main_menu(),
        )

    @bot.message_handler(commands=['help'])
    def cmd_help(msg: Message):
        bot.send_message(
            msg.chat.id,
            "📖 *Справка*\n\n"
            "*/add* — Пошаговый ввод данных за сегодня:\n"
            "  1\\. Настроение \\(1–5\\)\n"
            "  2\\. Часы работы/учёбы\n"
            "  3\\. Часы сна\n"
            "  4\\. Комментарий \\(опционально\\)\n\n"
            "*/stats* — Статистика за неделю, месяц, инсайты и графики\n"
            "*/history* — Последние 10 записей\n"
            "*/settings* — Изменить время напоминания\n"
            "*/clear* — Удалить все твои записи",
            parse_mode='MarkdownV2',
            reply_markup=main_menu(),
        )

    @bot.message_handler(commands=['add'])
    def cmd_add(msg: Message):
        get_or_create_user(msg.from_user.id, msg.from_user.username)
        _reset(msg.from_user.id)
        bot.send_message(
            msg.chat.id,
            "📝 *Шаг 1 из 4 — Настроение*\n\nОцени своё настроение сегодня:",
            parse_mode='Markdown',
            reply_markup=mood_keyboard(),
        )

    @bot.message_handler(commands=['stats'])
    def cmd_stats(msg: Message):
        get_or_create_user(msg.from_user.id, msg.from_user.username)
        bot.send_message(
            msg.chat.id,
            "📊 *Статистика*\n\nЧто хочешь узнать?",
            parse_mode='Markdown',
            reply_markup=stats_menu_keyboard(),
        )

    @bot.message_handler(commands=['history'])
    def cmd_history(msg: Message):
        get_or_create_user(msg.from_user.id, msg.from_user.username)
        entries = get_history(msg.from_user.id, 10)
        if not entries:
            bot.send_message(
                msg.chat.id,
                "📋 История пуста. Добавь первую запись: /add",
                reply_markup=main_menu(),
            )
            return
        lines = ["📋 *Последние 10 записей:*\n"]
        for e in entries:
            d       = e['entry_date'].strftime('%d.%m.%Y')
            emoji   = MOOD_EMOJI.get(e['mood'], '🙂')
            comment = f" — _{e['comment']}_" if e['comment'] else ''
            lines.append(
                f"*{d}*: {emoji} {e['mood']}/5 | "
                f"💼 {e['work_hours']}ч | 😴 {e['sleep_hours']}ч{comment}"
            )
        bot.send_message(
            msg.chat.id,
            '\n'.join(lines),
            parse_mode='Markdown',
            reply_markup=main_menu(),
        )

    @bot.message_handler(commands=['settings'])
    def cmd_settings(msg: Message):
        get_or_create_user(msg.from_user.id, msg.from_user.username)
        reminder = get_reminder(msg.from_user.id)
        rt      = str(reminder['reminder_time'])[:5] if reminder and reminder['reminder_time'] else '20:00'
        enabled = reminder['reminder_enabled'] if reminder else True
        status  = '✅ включено' if enabled else '❌ отключено'
        _set_state(msg.from_user.id, _REMINDER)
        bot.send_message(
            msg.chat.id,
            f"⚙️ *Настройки напоминаний*\n\n"
            f"Текущее время: *{rt}* ({status})\n\n"
            f"Введи новое время в формате *ЧЧ:ММ* (например, 21:30)\n"
            f"Или напиши *выкл*, чтобы отключить напоминания.",
            parse_mode='Markdown',
            reply_markup=main_menu(),
        )

    @bot.message_handler(commands=['clear'])
    def cmd_clear(msg: Message):
        get_or_create_user(msg.from_user.id, msg.from_user.username)
        bot.send_message(
            msg.chat.id,
            "⚠️ *Удаление данных*\n\n"
            "Ты уверен? Все твои записи будут удалены без возможности восстановления.",
            parse_mode='Markdown',
            reply_markup=confirm_clear_keyboard(),
        )

    @bot.callback_query_handler(func=lambda c: True)
    def handle_callback(call: CallbackQuery):
        uid  = call.from_user.id
        data = call.data
        cid  = call.message.chat.id
        mid  = call.message.message_id

        if data.startswith('mood_'):
            mood = int(data.split('_')[1])
            _udata(uid)['mood'] = mood
            bot.edit_message_text(
                f"✅ Настроение: {MOOD_EMOJI[mood]} {mood}/5",
                cid, mid,
            )
            bot.send_message(
                cid,
                "💼 *Шаг 2 из 4 — Работа/учёба*\n\n"
                "Сколько часов ты потратил на полезную работу/учёбу?",
                parse_mode='Markdown',
                reply_markup=work_hours_keyboard(),
            )

        elif data.startswith('work_') and data != 'work_custom':
            hours = float(data.split('_', 1)[1])
            _udata(uid)['work_hours'] = hours
            bot.edit_message_text(f"✅ Работа/учёба: 💼 {hours} ч", cid, mid)
            bot.send_message(
                cid,
                "😴 *Шаг 3 из 4 — Сон*\n\nСколько часов ты спал?",
                parse_mode='Markdown',
                reply_markup=sleep_hours_keyboard(),
            )

        elif data == 'work_custom':
            _set_state(uid, _WORK_CUSTOM)
            bot.edit_message_text(
                "💼 Введи количество часов работы/учёбы числом (например: 3.5):",
                cid, mid,
            )

        elif data.startswith('sleep_') and data != 'sleep_custom':
            hours = float(data.split('_', 1)[1])
            _udata(uid)['sleep_hours'] = hours
            bot.edit_message_text(f"✅ Сон: 😴 {hours} ч", cid, mid)
            bot.send_message(
                cid,
                "💬 *Шаг 4 из 4 — Комментарий*\n\n"
                "Хочешь добавить комментарий к этому дню?",
                parse_mode='Markdown',
                reply_markup=skip_keyboard(),
            )
            _set_state(uid, _COMMENT)

        elif data == 'sleep_custom':
            _set_state(uid, _SLEEP_CUSTOM)
            bot.edit_message_text(
                "😴 Введи количество часов сна числом (например: 7.5):",
                cid, mid,
            )

        elif data == 'skip_comment':
            _set_state(uid, _IDLE)
            bot.edit_message_text("✅ Комментарий пропущен.", cid, mid)
            _save_entry(bot, uid, cid, comment=None)

        elif data == 'stats_week':
            bot.answer_callback_query(call.id)
            _show_stats(bot, uid, cid, days=7, label='неделю')
            return

        elif data == 'stats_month':
            bot.answer_callback_query(call.id)
            _show_stats(bot, uid, cid, days=30, label='месяц')
            return

        elif data == 'stats_insights':
            bot.answer_callback_query(call.id)
            _show_insights(bot, uid, cid)
            return

        elif data == 'stats_graph':
            bot.edit_message_text(
                "📉 Выбери период для графика:",
                cid, mid,
                reply_markup=graph_period_keyboard(),
            )

        elif data == 'graph_week':
            bot.answer_callback_query(call.id)
            try:
                bot.delete_message(cid, mid)
            except Exception:
                pass
            _send_graph(bot, uid, cid, days=7, label='7 дней')
            return

        elif data == 'graph_month':
            bot.answer_callback_query(call.id)
            try:
                bot.delete_message(cid, mid)
            except Exception:
                pass
            _send_graph(bot, uid, cid, days=30, label='30 дней')
            return

        elif data == 'confirm_clear':
            delete_user_data(uid)
            bot.edit_message_text("🗑 Все твои записи удалены.", cid, mid)

        elif data == 'cancel_clear':
            bot.edit_message_text("✅ Отмена. Данные не тронуты.", cid, mid)

        bot.answer_callback_query(call.id)

    @bot.message_handler(func=lambda m: True)
    def handle_text(msg: Message):
        uid   = msg.from_user.id
        state = _state(uid)
        text  = msg.text.strip() if msg.text else ''

        if text == '➕ Записать день':
            cmd_add(msg)
            return
        if text == '📊 Статистика':
            cmd_stats(msg)
            return
        if text == '📋 История':
            cmd_history(msg)
            return
        if text == '⚙️ Настройки':
            cmd_settings(msg)
            return

        if state == _WORK_CUSTOM:
            try:
                hours = float(text.replace(',', '.'))
                if not (0 <= hours <= 24):
                    raise ValueError
                _udata(uid)['work_hours'] = hours
                _set_state(uid, _IDLE)
                bot.send_message(
                    msg.chat.id,
                    f"✅ Работа/учёба: 💼 {hours} ч\n\n"
                    "😴 *Шаг 3 из 4 — Сон*\n\nСколько часов ты спал?",
                    parse_mode='Markdown',
                    reply_markup=sleep_hours_keyboard(),
                )
            except ValueError:
                bot.send_message(msg.chat.id, "⚠️ Введи число от 0 до 24 (например: 3.5)")

        elif state == _SLEEP_CUSTOM:
            try:
                hours = float(text.replace(',', '.'))
                if not (0 <= hours <= 24):
                    raise ValueError
                _udata(uid)['sleep_hours'] = hours
                _set_state(uid, _COMMENT)
                bot.send_message(
                    msg.chat.id,
                    f"✅ Сон: 😴 {hours} ч\n\n"
                    "💬 *Шаг 4 из 4 — Комментарий*\n\nХочешь добавить комментарий?",
                    parse_mode='Markdown',
                    reply_markup=skip_keyboard(),
                )
            except ValueError:
                bot.send_message(msg.chat.id, "⚠️ Введи число от 0 до 24 (например: 7.5)")

        elif state == _COMMENT:
            _set_state(uid, _IDLE)
            _save_entry(bot, uid, msg.chat.id, comment=text)

        elif state == _REMINDER:
            _set_state(uid, _IDLE)
            if text.lower() in ('выкл', 'откл', 'off', 'disable'):
                update_reminder(uid, '20:00', enabled=False)
                bot.send_message(msg.chat.id, "🔕 Напоминания отключены.", reply_markup=main_menu())
            elif re.match(r'^\d{1,2}:\d{2}$', text):
                try:
                    h, m = map(int, text.split(':'))
                    if not (0 <= h <= 23 and 0 <= m <= 59):
                        raise ValueError
                    update_reminder(uid, f'{h:02d}:{m:02d}', enabled=True)
                    bot.send_message(
                        msg.chat.id,
                        f"✅ Напоминание установлено на *{h:02d}:{m:02d}*",
                        parse_mode='Markdown',
                        reply_markup=main_menu(),
                    )
                except ValueError:
                    bot.send_message(
                        msg.chat.id,
                        "⚠️ Неверное время. Попробуй ещё раз: /settings",
                        reply_markup=main_menu(),
                    )
            else:
                bot.send_message(
                    msg.chat.id,
                    "⚠️ Формат: ЧЧ:ММ (например, 21:30). Попробуй: /settings",
                    reply_markup=main_menu(),
                )

        else:
            bot.send_message(
                msg.chat.id,
                "Используй команды или кнопки меню. /help — справка.",
                reply_markup=main_menu(),
            )
