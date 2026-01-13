from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "academics_department"

    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassRoom(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="classrooms")

    class Meta:
        db_table = "academics_classroom"

    def __str__(self):
        return f"{self.name} ({self.department.code})"


class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    credits = models.PositiveIntegerField()

    class Meta:
        db_table = "academics_course"

    def __str__(self):
        return f"{self.code} - {self.name}"
