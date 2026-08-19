from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import CheckInViewSet, GamificationSummaryView, HabitViewSet, ProgressReportView

router = DefaultRouter()
router.register("habits", HabitViewSet, basename="habit")
router.register("checkins", CheckInViewSet, basename="checkin")

urlpatterns = router.urls + [
    path("gamification/summary/", GamificationSummaryView.as_view(), name="gamification-summary"),
    path("habits/report/pdf/", ProgressReportView.as_view(), name="progress-report-pdf"),
]