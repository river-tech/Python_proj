from django import forms
from django.core.exceptions import ValidationError

from apps.academics.models import Course
from apps.enrollments.models import Enrollment, Grade
from apps.students.models import StudentProfile


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "semester"]
        labels = {
            "student": "Sinh viên",
            "course": "Môn học",
            "semester": "Học kỳ",
        }
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.TextInput(attrs={"class": "form-control", "placeholder": "VD: 2024-1"}),
        }

    def __init__(self, *args, **kwargs):
        self.fixed_student = kwargs.pop("student", None)
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = StudentProfile.objects.select_related("user", "classroom").all()
        self.fields["course"].queryset = Course.objects.all()

        if self.fixed_student:
            self.fields["student"].queryset = StudentProfile.objects.filter(pk=self.fixed_student.pk)
            self.fields["student"].initial = self.fixed_student
            self.fields["student"].widget = forms.HiddenInput()

    def clean(self):
        cleaned = super().clean()
        student = cleaned.get("student") or self.fixed_student
        course = cleaned.get("course")
        semester = cleaned.get("semester")
        if student and course and semester:
            qs = Enrollment.objects.filter(student=student, course=course, semester=semester)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Sinh viên đã đăng ký môn này trong học kỳ này.")
        cleaned["student"] = student
        return cleaned


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["score"]
        labels = {"score": "Điểm"}
        widgets = {"score": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10, "step": "0.1"})}
