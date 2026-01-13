from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("students/", include("apps.students.urls")),
    path("academics/", include("apps.academics.urls")),
    path("enrollments/", include("apps.enrollments.urls")),
    path("", include("apps.students.urls")),
]
