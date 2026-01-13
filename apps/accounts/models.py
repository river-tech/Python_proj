from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, role="STUDENT", **extra_fields):
        if not username:
            raise ValueError("Username is required")
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            role=role,
            is_active=extra_fields.pop("is_active", True),
            is_staff=extra_fields.pop("is_staff", False),
            date_joined=extra_fields.pop("date_joined", timezone.now()),
        )
        if password:
            user.set_password(password)
        else:
            user.password = ""
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, email=None, **extra_fields):
        return self.create_user(
            username=username,
            password=password,
            email=email,
            role=User.Role.ADMIN,
            is_active=True,
            is_staff=True,
            **extra_fields,
        )


class User(AbstractBaseUser):
    """
    DB-first user mapping to accounts_user (managed=False).
    Only uses columns that already exist in the database.
    """

    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"
        ADMIN = "ADMIN", "Admin"

    last_login = None  # disable last_login column (not present in DB)

    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = "accounts_user"

    @property
    def is_superuser(self):
        return self.role == self.Role.ADMIN

    def has_perm(self, perm, obj=None):
        return self.is_superuser or self.is_staff

    def has_module_perms(self, app_label):
        return self.is_superuser or self.is_staff

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return f"{self.username} ({self.role})"
