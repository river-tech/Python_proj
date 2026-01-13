from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import is_admin, is_student, is_teacher, role_required
from apps.academics.models import Course, Department
from apps.enrollments.models import Enrollment
from apps.students.forms import StudentProfileForm
from apps.students.models import StudentProfile


@login_required
def dashboard(request):
    context = {
        "total_students": StudentProfile.objects.count(),
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
        "total_departments": Department.objects.count(),
    }
    return render(request, "dashboard.html", context)


@login_required
def student_list(request):
    if is_student(request.user):
        students = StudentProfile.objects.select_related("user", "classroom__department").filter(
            user=request.user
        )
    else:
        students = StudentProfile.objects.select_related("user", "classroom__department").all()
    return render(request, "students/student_list.html", {"students": students})


@login_required
def student_detail(request, pk):
    student = get_object_or_404(StudentProfile.objects.select_related("user", "classroom__department"), pk=pk)
    if is_student(request.user) and student.user_id != request.user.id:
        raise PermissionDenied("Bạn không thể xem hồ sơ của người khác.")
    return render(request, "students/student_detail.html", {"student": student})


@login_required
@role_required(["ADMIN", "TEACHER"])
def student_create(request):
    form = StudentProfileForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        student = form.save(commit=False)
        # Ensure selected user is marked as student
        if hasattr(student.user, "role") and student.user.role != student.user.Role.STUDENT:
            student.user.role = student.user.Role.STUDENT
            student.user.save(update_fields=["role"])
        student.save()
        messages.success(request, "Student created successfully.")
        return redirect("students:detail", pk=student.pk)
    return render(request, "students/student_form.html", {"form": form, "form_title": "Create Student"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def student_update(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    form = StudentProfileForm(request.POST or None, instance=student)
    if request.method == "POST" and form.is_valid():
        student = form.save(commit=False)
        if hasattr(student.user, "role") and student.user.role != student.user.Role.STUDENT:
            student.user.role = student.user.Role.STUDENT
            student.user.save(update_fields=["role"])
        student.save()
        messages.success(request, "Student updated successfully.")
        return redirect("students:detail", pk=student.pk)
    return render(request, "students/student_form.html", {"form": form, "form_title": "Update Student"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def student_delete(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully.")
        return redirect("students:list")
    return render(request, "students/student_confirm_delete.html", {"student": student})
