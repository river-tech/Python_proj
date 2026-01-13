# Student Management System (Django MVC)

## 1) Project Overview
- **Mục tiêu:** Xây dựng **Hệ thống Quản lý Sinh viên (Student Management System)** cho phép quản lý sinh viên, khoa/lớp, môn học, đăng ký môn và điểm số. Hệ thống theo hướng **API-first** sử dụng **Django + Django REST Framework + JWT (SimpleJWT)**.
- **Vai trò:**
  - **Student:** đăng nhập, xem hồ sơ cá nhân, xem môn đã đăng ký, xem điểm.
  - **Teacher:** xem danh sách sinh viên theo lớp/môn, nhập/cập nhật điểm (MVP có thể để Admin thực hiện).
  - **Admin:** quản trị sinh viên, khoa/lớp, môn học, đăng ký môn, điểm số.
- **Mô hình MVC (Django MTV):**
  - **Model (M):** Django models (schema, ràng buộc dữ liệu).
  - **View (V):** UI (React hoặc Django Template) – chỉ hiển thị, không chứa nghiệp vụ.
  - **Controller (C):** DRF ViewSet/APIView + Router điều phối request → service layer → response.

---

## 2) Features (MVP)
- **Auth:** Register / Login / Refresh JWT (SimpleJWT).
- **Students:** CRUD sinh viên, hồ sơ cá nhân.
- **Departments & Classes:** quản lý khoa và lớp.
- **Courses:** quản lý môn học (tín chỉ).
- **Enrollment:** sinh viên đăng ký môn học.
- **Grades:** nhập và xem điểm.
- **Permission:** phân quyền theo role (STUDENT / TEACHER / ADMIN).

---

## 3) System Architecture
- **Phân tầng MVC/MTV:**
  - Model: `apps/*/models.py`
  - View (UI): `templates/`, `static/`, hoặc `frontend/` (React) – chỉ hiển thị.
  - Controller: DRF ViewSet/APIView + routers trong `apps/*/views.py` và `apps/*/urls.py`; gọi nghiệp vụ tại `apps/*/services.py`.
- **Apps/Modules (trong thư mục `apps/`):**
  - `apps/accounts`: auth, user, role.
  - `apps/academics`: khoa, lớp, môn học.
  - `apps/students`: hồ sơ sinh viên.
  - `apps/enrollments`: đăng ký môn, điểm số.
- **API-first:** DRF là Controller chính; UI chỉ tiêu thụ API.
- **Service layer:** đặt trong `services.py` của từng app (VD: đăng ký môn, tính GPA).

---

## 4) Data Model (Database Schema)
- **User (Django User / AbstractUser):**
  - `username`, `email`, `password`
  - `role` (choices: STUDENT, TEACHER, ADMIN)
- **StudentProfile:**
  - `user (OneToOne User)`
  - `student_code`
  - `class_room (FK ClassRoom)`
  - `date_of_birth`
- **Department:**
  - `name`, `code`
- **ClassRoom:**
  - `name`, `department (FK Department)`
- **Course:**
  - `name`, `code`, `credits`
- **Enrollment:**
  - `student (FK StudentProfile)`
  - `course (FK Course)`
  - `semester`
- **Grade:**
  - `enrollment (OneToOne Enrollment)`
  - `score`

---

## 5) API Specification
| Method | Endpoint | Auth | Mô tả |
|------|---------|------|------|
| POST | /api/auth/register | Public | Đăng ký |
| POST | /api/auth/login | Public | Đăng nhập |
| POST | /api/auth/refresh | Public | Refresh token |
| GET | /api/students/me | Student | Xem hồ sơ |
| GET | /api/courses | Public | Danh sách môn |
| POST | /api/enrollments | Student | Đăng ký môn |
| GET | /api/enrollments/my | Student | Môn đã đăng ký |
| POST | /api/grades | Admin/Teacher | Nhập điểm |

---

## 6) Business Rules
- Mỗi sinh viên **không đăng ký trùng môn trong cùng học kỳ**.
- Điểm chỉ nhập cho enrollment tồn tại.
- Quyền truy cập dựa trên role.

---

## 7) Local Development Setup
### Yêu cầu
- Python 3.10+
- pip, venv

### Khởi tạo & Cấu hình
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt python-dotenv psycopg2-binary

# Tạo project và apps bên trong thư mục apps/
django-admin startproject config .
mkdir -p apps
python manage.py startapp accounts apps/accounts
python manage.py startapp academics apps/academics
python manage.py startapp students apps/students
python manage.py startapp enrollments apps/enrollments

# Thêm vào INSTALLED_APPS trong config/settings.py:
# "apps.accounts", "apps.academics", "apps.students", "apps.enrollments",
# Thêm REST_FRAMEWORK và SIMPLE_JWT như hướng dẫn.

# Database: dùng PostgreSQL qua biến môi trường hoặc mặc định SQLite.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- Env: tạo `.env` (sao chép từ `.env.example`), chứa `SECRET_KEY`, `DEBUG`, cấu hình Postgres.

---

## 8) Project Structure
```
student_management/
│
├── manage.py
├── README.md
├── .env
├── .env.example
│
├── config/                     # Cấu hình hệ thống
│   ├── __init__.py
│   ├── settings.py             # Cấu hình Django
│   ├── urls.py                 # Router cấp hệ thống (Controller level)
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/                       # Chứa toàn bộ module nghiệp vụ
│   │
│   ├── accounts/               # Quản lý người dùng
│   │   ├── __init__.py
│   │   ├── models.py           # MODEL
│   │   ├── serializers.py
│   │   ├── views.py            # CONTROLLER
│   │   ├── urls.py             # CONTROLLER (routing)
│   │   ├── permissions.py
│   │   └── tests.py
│   │
│   ├── students/               # Sinh viên
│   │   ├── __init__.py
│   │   ├── models.py           # MODEL
│   │   ├── serializers.py
│   │   ├── services.py         # BUSINESS LOGIC (thuộc Controller)
│   │   ├── views.py            # CONTROLLER
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── academics/              # Khoa, lớp, môn học
│   │   ├── __init__.py
│   │   ├── models.py           # MODEL
│   │   ├── serializers.py
│   │   ├── services.py         # BUSINESS LOGIC
│   │   ├── views.py            # CONTROLLER
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── enrollments/            # Đăng ký môn & điểm
│   │   ├── __init__.py
│   │   ├── models.py           # MODEL
│   │   ├── serializers.py
│   │   ├── services.py         # BUSINESS LOGIC (đăng ký, kiểm tra trùng)
│   │   ├── views.py            # CONTROLLER
│   │   ├── urls.py
│   │   └── tests.py
│
├── templates/                  # VIEW (nếu dùng Django Template)
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── students/
│       └── profile.html
│
├── static/                     # CSS, JS, images (nếu dùng template)
│   ├── css/
│   └── js/
│
├── frontend/                   # VIEW (nếu dùng React)
│   ├── src/
│   └── package.json
│
└── requirements.txt
```
- Service layer ở `apps/*/services.py`; Controller (DRF) gọi vào service, giữ serializer mỏng.
- Templates/Static/Frontend là tùy chọn cho phần View; API vẫn hoạt động không cần UI.
