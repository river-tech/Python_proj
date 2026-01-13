from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.academics.models import Course
from apps.students.models import StudentProfile


class Enrollment(models.Model):
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    semester = models.CharField(max_length=20)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "enrollments_enrollment"
        unique_together = (("student", "course", "semester"),)

    def __str__(self):
        return f"{self.student.student_code} - {self.course.code} ({self.semester})"


class Grade(models.Model):
    id = models.BigAutoField(primary_key=True)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="grade")
    score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "enrollments_grade"

    def __str__(self):
        return f"{self.enrollment} -> {self.score}"
