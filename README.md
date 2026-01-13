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
- **Apps/Modules:**
  - `accounts`: auth, user, role.
  - `academics`: khoa, lớp, môn học.
  - `students`: hồ sơ sinh viên.
  - `enrollments`: đăng ký môn, điểm số.
- **API-first:** DRF là Controller chính; UI chỉ tiêu thụ API.
- **Service layer:** đặt trong `services.py` của từng app để chứa nghiệp vụ (VD: đăng ký môn, tính GPA).

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

### Khởi tạo
```bash
python -m venv venv
source venv/bin/activate
pip install django djangorestframework djangorestframework-simplejwt python-dotenv
django-admin startproject config .
python manage.py startapp accounts
python manage.py startapp academics
python manage.py startapp students
python manage.py startapp enrollments