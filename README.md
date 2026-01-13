# Student Management System – Full Django Template (MVC)

## 1) Tổng quan
- Hệ thống Quản lý Sinh viên dùng **Django server-side rendering** (Django Template + Static), không dùng React/Vite. Áp dụng mô hình **MVC**: Model (schema), Controller (views/urls), View (templates/static).
- Chức năng chính: quản lý Sinh viên, Khoa/Lớp, Môn học, Đăng ký môn (Enrollment), Điểm (Grade), phân quyền theo role (STUDENT/TEACHER/ADMIN) dùng Django auth.

## 2) Kiến trúc MVC
- **Model:** `apps/*/models.py` (User/Role, Department, ClassRoom, Course, StudentProfile, Enrollment, Grade).
- **Controller:** `apps/*/views.py` (function/CBV), `apps/*/urls.py` (routing), optional `services.py` cho nghiệp vụ.
- **View:** Django Templates trong `templates/` (HTML) + `static/` (CSS/JS). `base.html` làm layout, kế thừa cho các trang con.

## 3) Cấu trúc thư mục (đang dùng)
```
student_management/
├── manage.py
├── README.md
├── .env                      # cấu hình môi trường (DEBUG, SECRET_KEY,...)
├── requirements.txt          # Django dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py           # cấu hình Django, TEMPLATE DIR, STATICFILES_DIRS
│   ├── urls.py               # router cấp hệ thống
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── models.py         # User/role (hoặc Profile)
│   │   ├── forms.py          # Login/Register form (nếu cần)
│   │   ├── views.py          # login/logout view
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── admin.py
│   │   └── tests.py
│   ├── students/
│   │   ├── __init__.py
│   │   ├── models.py         # StudentProfile
│   │   ├── forms.py          # ModelForm Student
│   │   ├── services.py       # nghiệp vụ (tùy chọn)
│   │   ├── views.py          # CRUD student
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests.py
│   ├── academics/
│   │   ├── __init__.py
│   │   ├── models.py         # Department, ClassRoom, Course
│   │   ├── forms.py
│   │   ├── services.py
│   │   ├── views.py          # CRUD department/class/course
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests.py
│   └── enrollments/
│       ├── __init__.py
│       ├── models.py         # Enrollment, Grade
│       ├── forms.py          # EnrollmentForm, GradeForm
│       ├── services.py
│       ├── views.py          # đăng ký môn, nhập điểm
│       ├── urls.py
│       ├── admin.py
│       └── tests.py
├── templates/
│   ├── base.html
│   ├── auth/
│   │   └── login.html
│   └── students/
│       └── profile.html
└── static/
    ├── css/
    └── js/
```

## 4) Setup dự án từ 0 (command cụ thể)
```bash
cd student_management
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install django python-dotenv
pip freeze > requirements.txt

django-admin startproject config .
mkdir -p apps
python manage.py startapp accounts apps/accounts
python manage.py startapp academics apps/academics
python manage.py startapp students apps/students
python manage.py startapp enrollments apps/enrollments
mkdir -p templates/auth templates/students static/css static/js
```
- `config/settings.py`:
  - `INSTALLED_APPS` thêm: `apps.accounts`, `apps.academics`, `apps.students`, `apps.enrollments`.
  - `TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]`.
  - `STATIC_URL = "static/"`, `STATICFILES_DIRS = [BASE_DIR / "static"]`.
  - `LOGIN_URL = "/accounts/login/"`, `LOGIN_REDIRECT_URL = "/"`, `LOGOUT_REDIRECT_URL = "/accounts/login/"`.
  - Nếu custom user: `AUTH_USER_MODEL = "accounts.User"`.
- Chạy:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- `.env` (copy từ `.env.example` nếu có): `DEBUG=True`, `SECRET_KEY=change-me`, DB config (mặc định SQLite, có thể Postgres).

## 5) Models & Chức năng
- **Accounts/User:** dùng Django auth, thêm role (STUDENT/TEACHER/ADMIN). Có thể custom User hoặc Profile.
- **Students:** `StudentProfile(user, student_code, class_room, date_of_birth)`.
- **Academics:** `Department(name, code)`, `ClassRoom(name, department)`, `Course(name, code, credits)`.
- **Enrollments:** `Enrollment(student, course, semester)` với ràng buộc không trùng (unique_together). `Grade(enrollment, score)`.
- **Chức năng chính:** login/logout, dashboard, CRUD student/department/class/course, tạo enrollment, nhập điểm, xem danh sách/chi tiết.

## 6) Routing
- `config/urls.py`: include các app.
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("students/", include("apps.students.urls")),
    path("academics/", include("apps.academics.urls")),
    path("enrollments/", include("apps.enrollments.urls")),
    path("", include("apps.students.urls")),  # dashboard/home
]
```
- `apps/accounts/urls.py`: login (LoginView với template `auth/login.html`), logout.
- `apps/students/urls.py`: list, detail, create, update, delete (CBV hoặc FBV).
- `apps/academics/urls.py`: CRUD departments/classes/courses.
- `apps/enrollments/urls.py`: tạo enrollment, list enrollment, grade entry.

## 7) Templates (View)
- `templates/base.html`: layout, navbar (Home, Students, Courses, Enrollments, Admin), flash messages `{% if messages %}` và `{% block content %}`.
- `templates/auth/login.html`: form login kế thừa `base.html`.
- `templates/dashboard.html` (tạo mới): tổng quan, link nhanh tới students/courses/enrollments.
- `templates/students/student_list.html`, `student_detail.html`, `student_form.html`, `student_confirm_delete.html`.
- `templates/academics/` (tạo): `department_list.html`, `department_form.html`, `class_list.html`, `class_form.html`, `course_list.html`, `course_form.html`.
- `templates/enrollments/` (tạo): `enrollment_list.html`, `enrollment_form.html`, `enrollment_detail.html`, `grade_form.html`.
- `templates/students/profile.html`: trang hồ sơ cá nhân (đã có).

## 8) Forms & Validation
- Dùng `forms.py`/`ModelForm` cho create/update.
- Rule không đăng ký trùng môn trong cùng học kỳ:
  - Model `Enrollment` đặt `unique_together = ("student", "course", "semester")`.
  - `EnrollmentForm.clean()` kiểm tra tồn tại bản ghi trùng → `ValidationError`.
- `GradeForm`: validate điểm (0–10 hoặc theo thang).

## 9) Permissions & Auth
- Dùng Django auth: `LoginRequiredMixin`/`login_required`.
- Role check: `UserPassesTestMixin` hoặc decorator tự viết kiểm tra `user.role`.
- Student: chỉ xem hồ sơ của mình + enrollment/grade của mình.
- Teacher/Admin: nhập điểm; Admin full CRUD.
- `accounts/views.py`: dùng `LoginView`, `LogoutView` hoặc custom để set role redirect.

## 10) Admin site
- Đăng ký models tại `apps/*/admin.py`.
- Thêm `list_display`, `search_fields`, `list_filter` (vd Course: name, code; StudentProfile: user, student_code, class_room).
- Có thể inline Enrollment/Grade trong admin để nhập nhanh.

## 11) Definition of Done
- Server chạy với `python manage.py runserver`.
- Login/logout hoạt động.
- CRUD Students/Departments/Class/Course qua template form.
- Enrollment tạo được, rule không trùng cùng môn-học-kỳ hoạt động (constraint + validation).
- Nhập/xem điểm chạy được.
- Có seed/demo (tạo qua admin hoặc fixture) để duyệt giao diện.
