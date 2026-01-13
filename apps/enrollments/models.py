from django.db import models
from apps.students.models import StudentProfile
from apps.academics.models import Course


class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    semester = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "enrollments_enrollment"
        constraints = [
            models.UniqueConstraint(fields=["student", "course", "semester"], name="unique_enrollment_per_semester")
        ]

    def __str__(self):
        return f"{self.student.student_code} - {self.course.code} ({self.semester})"


class Grade(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="grade")
    score = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollments_grade"

    def __str__(self):
        return f"{self.enrollment} -> {self.score}"
