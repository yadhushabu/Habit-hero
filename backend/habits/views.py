from django.shortcuts import render

# Create your views here.
from datetime import date

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .gamification import level_for_xp
from .models import CheckIn, Habit
from .serializers import CheckInSerializer, HabitSerializer
import io
from datetime import date
from django.http import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


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

class GamificationSummaryView(APIView):
    def get(self, request):
        habits = Habit.objects.all()
        total_xp = sum(h.xp for h in habits)
        level_info = level_for_xp(total_xp)

        all_badges = {}
        for h in habits:
            for b in h.badges:
                all_badges[b["code"]] = b

        return Response({
            "total_xp": total_xp,
            **level_info,
            "badges": list(all_badges.values()),
            "badge_count": len(all_badges),
        })

class ProgressReportView(APIView):
    def get(self, request):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("Habit Hero - Progress Report", styles["Title"]))
        elements.append(Paragraph(f"Generated on {date.today().isoformat()}", styles["Normal"]))
        elements.append(Spacer(1, 20))


        data = [["Habit", "Category", "Frequency", "Current Streak", "Best Streak", "Success Rate", "XP"]]
        for habit in Habit.objects.all():
            data.append([
                habit.name,
                habit.get_category_display(),
                habit.get_frequency_display(),
                str(habit.current_streak),
                str(habit.best_streak),
                f"{habit.success_rate}%",
                str(habit.xp),
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="habit_progress_report.pdf")