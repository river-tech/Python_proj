from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.accounts.forms import LoginForm, RegisterForm, TeacherCreateForm
from apps.accounts.permissions import role_required


class AccountLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    next_page = "accounts:login"


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Đăng ký thành công, hãy đăng nhập.")
            # Optionally log user in right away:
            login(request, user, backend="apps.accounts.backends.AccountUserBackend")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})


@login_required
@role_required(["ADMIN"])
def create_teacher(request):
    if request.method == "POST":
        form = TeacherCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã tạo giáo viên mới.")
            return redirect("accounts:create_teacher")
    else:
        form = TeacherCreateForm()
    return render(request, "accounts/teacher_form.html", {"form": form})
