from collections import Counter

from django.db import models

# Create your models here.

class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ]

    CATEGORY_CHOICES = [
        ("health", "Health"),
        ("work", "Work"),
        ("learning", "Learning"),
        ("fitness", "Fitness"),
        ("mental_health", "Mental Health"),
        ("productivity", "Productivity"),
    ]

    name = models.CharField(max_length=120)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="daily")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="health")
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def current_streak(self):
        from datetime import date, timedelta

        dates = self.checkins.values_list("date", flat=True)
        if not dates:
            return 0

        if self.frequency == "weekly":
            weeks = {d.isocalendar()[:2] for d in dates}
            streak = 0
            cursor_week = date.today().isocalendar()[:2]
            cursor = date.today()
            if cursor_week not in weeks:
                cursor -= timedelta(weeks=1)
                cursor_week = cursor.isocalendar()[:2]
            while cursor_week in weeks:
                streak += 1
                cursor -= timedelta(weeks=1)
                cursor_week = cursor.isocalendar()[:2]
            return streak

        dates_set = set(dates)
        streak = 0
        cursor = date.today()
        if cursor not in dates_set:
            cursor -= timedelta(days=1)
        while cursor in dates_set:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    @property
    def best_streak(self):
        if self.frequency == "weekly":
            from datetime import date

            week_starts = sorted(
                date.fromisocalendar(*d.isocalendar()[:2], 1)
                for d in set(self.checkins.values_list("date", flat=True))
            )
            if not week_starts:
                return 0

            best = current = 1
            for i in range(1, len(week_starts)):
                if (week_starts[i] - week_starts[i - 1]).days == 7:
                    current += 1
                    best = max(best, current)
                else:
                    current = 1
            return best

        dates = sorted(self.checkins.values_list("date", flat=True))
        if not dates:
            return 0

        best = current = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i - 1]).days == 1:
                current += 1
                best = max(best, current)
            else:
                current = 1
        return best

    @property
    def success_rate(self):
        from datetime import date

        if self.frequency == "weekly":
            weeks_elapsed = (date.today() - self.start_date).days // 7 + 1
            if weeks_elapsed <= 0:
                return 0.0
            weeks_checked_in = len(
                {d.isocalendar()[:2] for d in self.checkins.values_list("date", flat=True)}
            )
            rate = (weeks_checked_in / weeks_elapsed) * 100
            return round(min(rate, 100.0), 1)

        days_elapsed = (date.today() - self.start_date).days + 1
        if days_elapsed <= 0:
            return 0.0
        total_checkins = self.checkins.count()
        rate = (total_checkins / days_elapsed) * 100
        return round(min(rate, 100.0), 1)
    @property
    def best_days(self):
        weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekdays = [d.weekday() for d in self.checkins.values_list("date", flat=True)]
        if not weekdays:
            return []

        counts = Counter(weekdays)
        ranked = counts.most_common()
        top_count = ranked[0][1]
        return [weekday_names[day] for day, count in ranked if count == top_count]

    @property
    def xp(self):
        """10 XP per check-in + streak milestone bonuses."""
        base_xp = self.checkins.count() * 10
        best = self.best_streak
        milestone_bonus = sum(
            bonus for milestone, bonus in
            [(7, 50), (14, 75), (30, 150), (60, 300), (100, 500)]
            if best >= milestone
        )
        return base_xp + milestone_bonus

    @property
    def badges(self):
        from .gamification import BADGE_DEFINITIONS
        return [
            {"code": b["code"], "name": b["name"], "description": b["description"], "icon": b["icon"]}
            for b in BADGE_DEFINITIONS
            if b["condition"](self)
        ]

class CheckIn(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="checkins")
    date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("habit", "date")

    def __str__(self):
        return f"{self.habit.name} - {self.date}"