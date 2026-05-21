import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


_MOOD_COLORS  = '#FF6B6B'
_WORK_COLORS  = '#4ECDC4'
_SLEEP_COLORS = '#45B7D1'


def generate_stats_graph(entries: list, title: str = "Статистика") -> io.BytesIO | None:
    if not entries:
        return None

    dates  = [row['entry_date'] for row in entries]
    moods  = [float(row['mood'])        for row in entries]
    work   = [float(row['work_hours'])  for row in entries]
    sleep  = [float(row['sleep_hours']) for row in entries]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)

    # — Mood (line + fill) —
    axes[0].plot(dates, moods, 'o-', color=_MOOD_COLORS, linewidth=2, markersize=5)
    axes[0].fill_between(dates, moods, alpha=0.15, color=_MOOD_COLORS)
    axes[0].set_ylabel('Настроение', fontsize=10)
    axes[0].set_ylim(0.5, 5.5)
    axes[0].set_yticks([1, 2, 3, 4, 5])
    axes[0].grid(True, alpha=0.3)
    for x, y in zip(dates, moods):
        axes[0].annotate(str(int(y)), (x, y), textcoords='offset points',
                         xytext=(0, 6), ha='center', fontsize=8)

    # — Work hours (bar) —
    axes[1].bar(dates, work, color=_WORK_COLORS, alpha=0.85, width=0.6)
    axes[1].set_ylabel('Работа (ч)', fontsize=10)
    axes[1].grid(True, alpha=0.3, axis='y')

    # — Sleep hours (bar) —
    axes[2].bar(dates, sleep, color=_SLEEP_COLORS, alpha=0.85, width=0.6)
    axes[2].set_ylabel('Сон (ч)', fontsize=10)
    axes[2].grid(True, alpha=0.3, axis='y')

    # X-axis formatting
    interval = 3 if len(dates) > 14 else 1
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
    axes[2].xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf
