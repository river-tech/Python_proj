from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Tên đăng nhập"}),
    )
    password = forms.CharField(
        label="Mật khẩu",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mật khẩu"}),
    )


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mật khẩu"}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Nhập lại mật khẩu",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Nhập lại mật khẩu"}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tên đăng nhập"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        }

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Mật khẩu không khớp")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = getattr(User, "Role", None).STUDENT if hasattr(User, "Role") else "STUDENT"
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class TeacherCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mật khẩu"}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Nhập lại mật khẩu",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Nhập lại mật khẩu"}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tên đăng nhập"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
        }
        labels = {"username": "Tên đăng nhập", "email": "Email"}

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Mật khẩu không khớp")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # Teacher role, staff
        user.role = getattr(User, "Role", None).TEACHER if hasattr(User, "Role") else "TEACHER"
        user.is_staff = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
