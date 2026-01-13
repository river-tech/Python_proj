from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.students.models import StudentProfile
from apps.academics.models import Course, Department
from apps.enrollments.models import Enrollment


@login_required
def dashboard(request):
    context = {
        "total_students": StudentProfile.objects.count(),
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
        "total_departments": Department.objects.count(),
    }
    return render(request, "dashboard.html", context)
