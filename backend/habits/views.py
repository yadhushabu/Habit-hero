from django.shortcuts import render

# Create your views here.
from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CheckIn, Habit
from .serializers import CheckInSerializer, HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    @action(detail=True, methods=["post"])
    def check_in(self, request, pk=None):
        habit = self.get_object()
        checkin_date = request.data.get("date", date.today().isoformat())
        note = request.data.get("note", "")

        checkin, created = CheckIn.objects.get_or_create(
            habit=habit,
            date=checkin_date,
            defaults={"note": note},
        )

        serializer = HabitSerializer(habit)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CheckInViewSet(viewsets.ModelViewSet):
    queryset = CheckIn.objects.all()
    serializer_class = CheckInSerializer