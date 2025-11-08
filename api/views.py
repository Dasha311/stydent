from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.http import HttpResponse
import csv

from accounts.models import CustomUser
from courses.models import Course, Enrollment, LessonCompletion
from accounts.permissions import IsAdmin


class AdminAnalyticsView(APIView):
    """Simple analytics dashboard for admins."""

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        week_ago = timezone.now() - timedelta(days=7)

        new_students = CustomUser.objects.filter(
            role="student", date_joined__gte=week_ago
        ).count()
        active_students = CustomUser.objects.filter(
            role="student", last_login__gte=week_ago
        ).count()

        durations = []
        for enrollment in Enrollment.objects.filter(progress=100):
            completions = LessonCompletion.objects.filter(
                student=enrollment.student, lesson__course=enrollment.course
            ).order_by("completed_at")
            if completions.exists():
                delta = completions.last().completed_at - completions.first().completed_at
                durations.append(delta.total_seconds() / 86400)
        avg_completion = sum(durations) / len(durations) if durations else 0

        top_courses = (
            Course.objects.annotate(num=Count("enrollments"))
            .order_by("-num")[:5]
            .values_list("title", "num")
        )

        data = {
            "new_students_week": new_students,
            "active_students_week": active_students,
            "avg_completion_days": round(avg_completion, 2),
            "top_courses": list(top_courses),
        }

        if request.query_params.get("format") == "csv":
            response = HttpResponse(content_type="text/csv")
            writer = csv.writer(response)
            writer.writerow(["Metric", "Value"])
            writer.writerow(["New students this week", new_students])
            writer.writerow(["Active students this week", active_students])
            writer.writerow(["Average completion days", round(avg_completion, 2)])
            writer.writerow(["Top courses", ""])
            for title, num in top_courses:
                writer.writerow([title, num])
            return response

        return Response(data)
