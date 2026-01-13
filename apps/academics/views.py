from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import role_required
from apps.academics.forms import ClassRoomForm, CourseForm, DepartmentForm
from apps.academics.models import ClassRoom, Course, Department


@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "academics/department_list.html", {"departments": departments})


@login_required
@role_required(["ADMIN", "TEACHER"])
def department_create(request):
    form = DepartmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã tạo khoa.")
        return redirect("academics:department_list")
    return render(request, "academics/department_form.html", {"form": form, "form_title": "Create Department"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật khoa.")
        return redirect("academics:department_list")
    return render(request, "academics/department_form.html", {"form": form, "form_title": "Update Department"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        department.delete()
        messages.success(request, "Đã xóa khoa.")
    return redirect("academics:department_list")


@login_required
def classroom_list(request):
    classrooms = ClassRoom.objects.select_related("department").all()
    return render(request, "academics/classroom_list.html", {"classrooms": classrooms})


@login_required
@role_required(["ADMIN", "TEACHER"])
def classroom_create(request):
    form = ClassRoomForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã tạo lớp.")
        return redirect("academics:classroom_list")
    return render(request, "academics/classroom_form.html", {"form": form, "form_title": "Create Classroom"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def classroom_update(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    form = ClassRoomForm(request.POST or None, instance=classroom)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật lớp.")
        return redirect("academics:classroom_list")
    return render(request, "academics/classroom_form.html", {"form": form, "form_title": "Update Classroom"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def classroom_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    if request.method == "POST":
        classroom.delete()
        messages.success(request, "Đã xóa lớp.")
    return redirect("academics:classroom_list")


@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, "academics/course_list.html", {"courses": courses})


@login_required
@role_required(["ADMIN", "TEACHER"])
def course_create(request):
    form = CourseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã tạo môn học.")
        return redirect("academics:course_list")
    return render(request, "academics/course_form.html", {"form": form, "form_title": "Create Course"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, instance=course)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật môn học.")
        return redirect("academics:course_list")
    return render(request, "academics/course_form.html", {"form": form, "form_title": "Update Course"})


@login_required
@role_required(["ADMIN", "TEACHER"])
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Đã xóa môn học.")
    return redirect("academics:course_list")
