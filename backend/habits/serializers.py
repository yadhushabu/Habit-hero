from rest_framework import serializers

from .models import CheckIn, Habit


class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ["id", "habit", "date", "note", "created_at"]
        read_only_fields = ["id", "created_at"]


class HabitSerializer(serializers.ModelSerializer):
    current_streak = serializers.ReadOnlyField()
    best_streak = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    best_days = serializers.ReadOnlyField()
    checkins = CheckInSerializer(many=True, read_only=True)

    class Meta:
        model = Habit
        fields = [
            "id", "name", "frequency", "category", "start_date", "created_at",
            "current_streak", "best_streak", "success_rate", "best_days", "checkins",
        ]
        read_only_fields = ["id", "created_at"]