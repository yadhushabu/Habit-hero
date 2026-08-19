from rest_framework.routers import DefaultRouter

from .views import CheckInViewSet, HabitViewSet

router = DefaultRouter()
router.register("habits", HabitViewSet, basename="habit")
router.register("checkins", CheckInViewSet, basename="checkin")

urlpatterns = router.urls