-- test_data.sql
-- Тестовые данные: 1 пользователь, 15 записей за разные дни

INSERT INTO users (user_id, username, reminder_time, reminder_enabled)
VALUES (8108522195, 'test_user', '20:00', TRUE)
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO entries (user_id, entry_date, mood, work_hours, sleep_hours, comment) VALUES
(8108522195, CURRENT_DATE - INTERVAL '14 days', 3, 4.0, 7.0, 'Обычный день, ничего особенного'),
(8108522195, CURRENT_DATE - INTERVAL '13 days', 2, 6.5, 5.5, 'Много работы, устал'),
(8108522195 CURRENT_DATE - INTERVAL '12 days', 4, 3.0, 8.5, 'Хорошо выспался, продуктивно'),
(8108522195, CURRENT_DATE - INTERVAL '11 days', 5, 2.0, 9.0, 'Отличный день! Всё успел'),
(8108522195, CURRENT_DATE - INTERVAL '10 days', 3, 5.0, 6.5, NULL),
(8108522195, CURRENT_DATE - INTERVAL '9 days',  2, 7.0, 5.0, 'Дедлайн, почти не спал'),
(8108522195, CURRENT_DATE - INTERVAL '8 days',  1, 8.0, 4.5, 'Очень тяжёлый день'),
(8108522195, CURRENT_DATE - INTERVAL '7 days',  3, 4.5, 7.5, 'Выходной, немного поработал'),
(8108522195, CURRENT_DATE - INTERVAL '6 days',  4, 1.0, 9.0, 'Отдыхал, настроение хорошее'),
(8108522195, CURRENT_DATE - INTERVAL '5 days',  5, 3.5, 8.0, 'Занимался любимым проектом'),
(8108522195, CURRENT_DATE - INTERVAL '4 days',  4, 4.0, 8.0, NULL),
(8108522195, CURRENT_DATE - INTERVAL '3 days',  3, 5.5, 7.0, 'Средний день'),
(8108522195, CURRENT_DATE - INTERVAL '2 days',  2, 6.0, 6.0, 'Опять много задач'),
(8108522195, CURRENT_DATE - INTERVAL '1 day',   4, 3.0, 8.5, 'Хорошо отдохнул вечером'),
(8108522195, CURRENT_DATE,                       5, 2.5, 9.0, 'Сегодня всё прекрасно!')
ON CONFLICT (user_id, entry_date) DO NOTHING;
