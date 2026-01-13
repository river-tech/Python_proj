from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import is_admin, is_student, is_teacher, role_required
from apps.enrollments.forms import EnrollmentForm, GradeForm
from apps.enrollments.models import Enrollment, Grade
from apps.students.models import StudentProfile


@login_required
def enrollment_list(request):
    enrollments = Enrollment.objects.select_related("student__user", "course").all()
    if is_student(request.user):
        enrollments = enrollments.filter(student__user=request.user)
    return render(request, "enrollments/enrollment_list.html", {"enrollments": enrollments})


@login_required
@role_required(["STUDENT", "ADMIN", "TEACHER"])
def enrollment_create(request):
    student_profile = None
    if is_student(request.user):
        student_profile = StudentProfile.objects.filter(user=request.user).first()
        if not student_profile:
            messages.error(request, "Bạn cần hồ sơ sinh viên trước khi đăng ký môn.")
            return redirect("students:list")

    form = EnrollmentForm(request.POST or None, student=student_profile)
    if request.method == "POST" and form.is_valid():
        enrollment = form.save(commit=False)
        if student_profile:
            enrollment.student = student_profile
        enrollment.save()
        messages.success(request, "Đăng ký môn thành công.")
        return redirect("enrollments:detail", pk=enrollment.pk)
    return render(
        request,
        "enrollments/enrollment_form.html",
        {"form": form, "form_title": "Đăng ký môn"},
    )


@login_required
def enrollment_detail(request, pk):
    enrollment = get_object_or_404(Enrollment.objects.select_related("student__user", "course"), pk=pk)
    if is_student(request.user) and enrollment.student.user_id != request.user.id:
        raise PermissionDenied("Bạn không thể xem đăng ký của người khác.")
    return render(request, "enrollments/enrollment_detail.html", {"enrollment": enrollment})


@login_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if not (is_admin(request.user) or enrollment.student.user_id == request.user.id):
        raise PermissionDenied("Bạn không thể hủy đăng ký của người khác.")
    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Đã xóa đăng ký môn.")
    return redirect("enrollments:list")


@login_required
@role_required(["ADMIN", "TEACHER"])
def grade_update(request, pk):
    enrollment = get_object_or_404(Enrollment.objects.select_related("student__user", "course"), pk=pk)
    grade, _ = Grade.objects.get_or_create(enrollment=enrollment)
    form = GradeForm(request.POST or None, instance=grade)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật điểm.")
        return redirect("enrollments:detail", pk=enrollment.pk)
    return render(
        request,
        "enrollments/grade_form.html",
        {"form": form, "enrollment": enrollment},
    )
