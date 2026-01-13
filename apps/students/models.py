from django.conf import settings
from django.db import models

from apps.academics.models import ClassRoom


class StudentProfile(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
        db_constraint=True,
    )
    student_code = models.CharField(max_length=50, unique=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.RESTRICT, related_name="students")
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "students_studentprofile"

    def __str__(self):
        return f"{self.student_code} - {self.user.username}"
