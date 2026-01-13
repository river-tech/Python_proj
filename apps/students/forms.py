from django import forms
from django.contrib.auth import get_user_model

from apps.academics.models import ClassRoom
from apps.students.models import StudentProfile

User = get_user_model()


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["user", "student_code", "classroom", "date_of_birth"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(role=User.Role.STUDENT)
        self.fields["classroom"].queryset = ClassRoom.objects.select_related("department").all()
        self.fields["user"].widget.attrs.update({"class": "form-select"})
        self.fields["student_code"].widget.attrs.update({"class": "form-control"})
        self.fields["classroom"].widget.attrs.update({"class": "form-select"})
