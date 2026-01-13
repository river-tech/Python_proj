from django.db import models


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = "academics_department"

    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassRoom(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.RESTRICT, related_name="classrooms")

    class Meta:
        managed = False
        db_table = "academics_classroom"

    def __str__(self):
        return f"{self.name} ({self.department.code})"


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    credits = models.IntegerField()

    class Meta:
        managed = False
        db_table = "academics_course"

    def __str__(self):
        return f"{self.code} - {self.name}"
