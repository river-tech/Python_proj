from django import forms

from apps.academics.models import ClassRoom, Course, Department


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name", "code"]
        labels = {"name": "Tên khoa", "code": "Mã khoa"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập tên khoa"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập mã khoa"}),
        }


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ["name", "department"]
        labels = {"name": "Tên lớp", "department": "Khoa"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập tên lớp"}),
            "department": forms.Select(attrs={"class": "form-select"}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "code", "credits"]
        labels = {"name": "Tên môn học", "code": "Mã môn", "credits": "Số tín chỉ"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập tên môn học"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập mã môn"}),
            "credits": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }
