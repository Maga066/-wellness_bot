import pandas as pd
import matplotlib.pyplot as plt

def create_chart(records, filename):
    if len(records) < 2:
        return

    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])

    fig, ax1 = plt.subplots(figsize=(10, 5))

    color1 = '#FF6B6B'
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Настроение (1-5)', color=color1)
    ax1.plot(df['date'], df['mood'], 'o-', color=color1, linewidth=2, markersize=6, label='Настроение')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(0.5, 5.5)

    ax2 = ax1.twinx()
    color2 = '#4ECDC4'
    color3 = '#45B7D1'

    ax2.set_ylabel('Часы', color=color2)
    ax2.plot(df['date'], df['work_hours'], 's-', color=color2, linewidth=2, markersize=5, label='Работа')
    ax2.plot(df['date'], df['sleep_hours'], 'd-', color=color3, linewidth=2, markersize=5, label='Сон')
    ax2.tick_params(axis='y', labelcolor=color2)

    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    plt.title('Динамика самочувствия', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename, dpi=100, bbox_inches='tight')
    plt.close()


def get_insights(records):
    if not records:
        return "Нет данных."

    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])
    df['weekday'] = df['date'].dt.day_name()

    mood = round(df["mood"].mean(), 1)
    work = round(df["work_hours"].mean(), 1)
    sleep = round(df["sleep_hours"].mean(), 1)

    weekday_mood = df.groupby('weekday')['mood'].mean().sort_values(ascending=False)
    best_day = weekday_mood.index[0] if not weekday_mood.empty else "—"

    high_sleep = df[df["sleep_hours"] >= 7.5]["mood"].mean() if len(df[df["sleep_hours"] >= 7.5]) > 0 else mood
    low_sleep = df[df["sleep_hours"] < 7.5]["mood"].mean() if len(df[df["sleep_hours"] < 7.5]) > 0 else mood

    low_work = df[df["work_hours"] < 4]["mood"].mean() if len(df[df["work_hours"] < 4]) > 0 else mood
    high_work = df[df["work_hours"] >= 4]["mood"].mean() if len(df[df["work_hours"] >= 4]) > 0 else mood

    sleep_msg = "😴 Сон > 7.5ч улучшает настроение" if high_sleep > low_sleep else "😴 Сон не сильно влияет на настроение"
    work_msg = "💼 Работа < 4ч связана с лучшим настроением" if low_work > high_work else "💼 Работа не снижает настроение"

    return (
        f"📊 *Инсайты*\n\n"
        f"📈 Среднее за {len(df)} дней:\n"
        f"😊 Настроение: {mood}/5\n"
        f"💼 Работа: {work}ч\n"
        f"😴 Сон: {sleep}ч\n\n"
        f"🌟 Лучший день: {best_day}\n\n"
        f"{sleep_msg}\n"
        f"{work_msg}"
    )