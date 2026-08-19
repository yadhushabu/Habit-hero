from django.contrib import admin

# Register your models here.

from .models import CheckIn, Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ["name", "frequency", "category", "start_date", "current_streak", "success_rate"]


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ["habit", "date", "note"]