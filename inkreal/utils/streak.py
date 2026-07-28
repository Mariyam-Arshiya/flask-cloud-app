from datetime import datetime, timezone, timedelta


def calculate_streak(post_dates):
    if not post_dates:
        return {"current": 0, "longest": 0, "total_posts": 0}

    dates = set()
    for d in post_dates:
        try:
            if isinstance(d, str):
                dt = datetime.fromisoformat(d.replace("Z", "+00:00"))
            elif isinstance(d, (int, float)):
                dt = datetime.fromtimestamp(d / 1000, tz=timezone.utc)
            else:
                dt = d
            dates.add(dt.date())
        except (ValueError, AttributeError):
            continue

    if not dates:
        return {"current": 0, "longest": 0, "total_posts": len(post_dates)}

    sorted_dates = sorted(dates, reverse=True)
    today = datetime.now(timezone.utc).date()

    current_streak = 0
    check_date = today

    if sorted_dates[0] == today or sorted_dates[0] == today - timedelta(days=1):
        if sorted_dates[0] == today - timedelta(days=1):
            check_date = today - timedelta(days=1)

        for d in sorted_dates:
            if d == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif d < check_date:
                break

    longest_streak = 1
    temp_streak = 1
    all_sorted = sorted(dates)

    for i in range(1, len(all_sorted)):
        if all_sorted[i] - all_sorted[i - 1] == timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        elif all_sorted[i] != all_sorted[i - 1]:
            temp_streak = 1

    return {
        "current": current_streak,
        "longest": longest_streak,
        "total_posts": len(post_dates),
        "wrote_today": today in dates
    }


def get_streak_level(streak_count):
    if streak_count >= 365:
        return {"level": "Legendary", "emoji": "👑", "color": "#FFD700"}
    elif streak_count >= 100:
        return {"level": "Master", "emoji": "🔥", "color": "#FF4500"}
    elif streak_count >= 30:
        return {"level": "Dedicated", "emoji": "⚡", "color": "#4111CC"}
    elif streak_count >= 7:
        return {"level": "Consistent", "emoji": "✨", "color": "#2E86AB"}
    elif streak_count >= 3:
        return {"level": "Building", "emoji": "🌱", "color": "#28A745"}
    else:
        return {"level": "Starting", "emoji": "📝", "color": "#666"}
