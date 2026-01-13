from django.urls import path

from apps.enrollments import views

app_name = "enrollments"

urlpatterns = [
    path("", views.enrollment_list, name="list"),
    path("create/", views.enrollment_create, name="create"),
    path("<int:pk>/", views.enrollment_detail, name="detail"),
    path("<int:pk>/delete/", views.enrollment_delete, name="delete"),
    path("<int:pk>/grade/", views.grade_update, name="grade_update"),
]
