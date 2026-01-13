from django.db import models
from django.conf import settings
from apps.academics.models import ClassRoom


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    student_code = models.CharField(max_length=100, unique=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.RESTRICT, related_name="students")
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "students_studentprofile"

    def __str__(self):
        return f"{self.student_code} - {self.user.username}"
