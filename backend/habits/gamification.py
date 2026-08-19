BADGE_DEFINITIONS = [
    {
        "code": "first_step",
        "name": "First Step",
        "description": "Complete your first check-in",
        "icon": "🌱",
        "condition": lambda habit: habit.checkins.count() >= 1,
    },
    {
        "code": "week_warrior",
        "name": "Week Warrior",
        "description": "Reach a 7-day streak",
        "icon": "🔥",
        "condition": lambda habit: habit.best_streak >= 7,
    },
    {
        "code": "consistency_king",
        "name": "Consistency King",
        "description": "Reach a 30-day streak",
        "icon": "👑",
        "condition": lambda habit: habit.best_streak >= 30,
    },
    {
        "code": "century_club",
        "name": "Century Club",
        "description": "Log 100 check-ins",
        "icon": "💯",
        "condition": lambda habit: habit.checkins.count() >= 100,
    },
    {
        "code": "high_achiever",
        "name": "High Achiever",
        "description": "Maintain an 80%+ success rate",
        "icon": "⭐",
        "condition": lambda habit: habit.success_rate >= 80,
    },
]


def level_for_xp(xp):

    level = 1
    threshold = 100
    remaining = xp
    while remaining >= threshold:
        remaining -= threshold
        level += 1
        threshold += 100
    return {
        "level": level,
        "xp_into_level": remaining,
        "xp_for_next_level": threshold,
    }