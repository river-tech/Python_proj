# Student Management System – Full Django Template (MVC)

## 1. Giới thiệu dự án
- **Student Management System** là hệ thống quản lý sinh viên dùng server-side rendering (Django Template) cho phép quản lý hồ sơ sinh viên, khoa/lớp, môn học, đăng ký môn và nhập điểm.
- **Bài toán giải quyết:** tập trung hóa dữ liệu đào tạo, đơn giản hóa quy trình đăng ký môn, nhập điểm, và kiểm soát truy cập theo vai trò.
- **Đối tượng sử dụng:** Admin (toàn quyền), Teacher (nhập điểm, xem đăng ký), Student (đăng ký môn, xem điểm, hồ sơ).
- **Vì sao chọn Django Template (SSR), không dùng React:** giảm độ phức tạp triển khai, không phụ thuộc API tách biệt, render nhanh, bảo mật tốt hơn cho form/auth mặc định, phù hợp bài toán CRUD nội bộ.

## 2. Công nghệ sử dụng
- **Python 3.x:** ngôn ngữ chính.
- **Django:** framework web full-stack, cung cấp ORM, Auth, Admin.
- **Django Auth & Admin:** xác thực, phân quyền, bảng điều khiển quản trị.
- **PostgreSQL:** cơ sở dữ liệu quan hệ, an toàn, hỗ trợ khóa ngoại/constraint.
- **HTML/CSS (Django Template):** render SSR, dễ tùy biến giao diện.
- **Bootstrap 5:** bố cục và component UI nhanh, gọn gàng.

## 3. Kiến trúc tổng thể hệ thống
- **Mô hình MVC (Django MTV):**
  - **Model (M):** định nghĩa schema (managed=False) ánh xạ bảng có sẵn.
  - **Template (V):** HTML render giao diện.
  - **View (C):** xử lý request, nghiệp vụ, điều hướng.
- **Luồng request/response:** Browser → URLconf → View (Controller) → Model/ORM → Template → Response.
- **Lý do MVC phù hợp:** tách biệt rõ tầng hiển thị, nghiệp vụ và dữ liệu; dễ bảo trì, mở rộng vai trò người dùng.

## 4. Thiết kế Database & Data Flow
- **DB-first:** kết nối PostgreSQL có sẵn, không tạo migration nghiệp vụ; mô hình từ `inspectdb`, `managed=False`.
- **Bảng chính:**
  - `auth_user` (hoặc `accounts_user` DB-first): thông tin đăng nhập & vai trò.
  - `students_studentprofile`: hồ sơ sinh viên (user, mã SV, lớp, ngày sinh).
  - `academics_department`: khoa.
  - `academics_classroom`: lớp thuộc khoa.
  - `academics_course`: môn học.
  - `enrollments_enrollment`: đăng ký môn (student, course, semester, unique).
  - `enrollments_grade`: điểm cho mỗi enrollment (one-to-one).
- **Quan hệ:** User 1-1 StudentProfile; Department 1-N ClassRoom; Course độc lập; StudentProfile 1-N Enrollment; Enrollment 1-1 Grade.
- **ORM DB-first:** dùng `inspectdb` sinh model với `managed=False`, giữ `db_table` đúng tên bảng; ORM thao tác CRUD, tôn trọng constraint có sẵn.
- **Chống SQL Injection:** ORM tự escape tham số, hạn chế string concat; truy vấn dùng API ORM thay vì raw SQL.

## 5. Authentication & Authorization (Điểm mạnh Django)
- **Django Auth:**
  - Đăng nhập/đăng xuất qua session server-side.
  - Middleware xác thực tự động gắn `request.user`.
- **Phân quyền:** `is_superuser`/`is_staff` (Admin), role TEACHER/STUDENT (field `role`), decorator `login_required`, `role_required`.
- **Chính sách:**
  - **Admin:** toàn quyền CRUD, truy cập admin site.
  - **Teacher:** xem enrollment, nhập điểm, quản lý học thuật.
  - **Student:** xem hồ sơ, đăng ký môn, xem điểm của mình.

## 6. Logic nghiệp vụ chính
### 6.1 Students
- CRUD hồ sơ sinh viên (Admin/Teacher); Student chỉ xem hồ sơ của mình.
- Ràng buộc mã sinh viên và user 1-1.
### 6.2 Academics
- Quản lý Khoa/Lớp/Môn; thao tác bởi Admin/Teacher.
### 6.3 Enrollments
- Sinh viên đăng ký môn theo học kỳ; rule unique (student, course, semester) kiểm tra qua constraint + form validation.
- Teacher/Admin xem tất cả đăng ký.
### 6.4 Grades
- Teacher/Admin nhập/sửa điểm; mỗi Enrollment có một Grade.
- Student chỉ xem điểm của bản thân.

## 7. Giao diện (Template & UI Logic)
- `templates/base.html` là layout chính.
- **Chưa login:** giao diện auth shell, không sidebar, chỉ Login/Register.
- **Đã login:** sidebar và menu theo role (Admin/Teacher thấy menu học thuật).
- **Nguyên tắc UI:** gọn gàng, tone quản trị, dùng Bootstrap, tránh màu mè.

## 8. Bảo mật hệ thống
- CSRF protection cho form POST.
- Autoescape chống XSS.
- ORM chống SQL Injection.
- Password hashing qua Django Auth.
- Clickjacking protection (`X-Frame-Options` mặc định).
- Session security (cookie HttpOnly, server-side session).

## 9. Cách chạy dự án
```bash
git clone <repo>
cd student_management
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # điền DATABASE_URL PostgreSQL sẵn bảng

# Test kết nối DB
./.venv/bin/python manage.py dbshell <<'SQL'
SELECT 1;
SQL

# Chạy server
./.venv/bin/python manage.py runserver
```

## 10. Hướng dẫn demo & kiểm thử
- Tạo user: Admin/Teacher/Student (qua admin site hoặc script seed).
- URL cần thử:
  - `/accounts/login`
  - `/` (dashboard)
  - `/students/` (danh sách SV)
  - `/academics/courses/` (môn học)
  - `/enrollments/` (đăng ký)
  - `/admin/` (admin site)
- Checklist:
  - Đăng nhập từng vai trò.
  - Student: xem hồ sơ, đăng ký môn, xem điểm.
  - Teacher: xem đăng ký, nhập điểm.
  - Admin: CRUD tất cả entities.

## 11. Hạn chế & hướng phát triển
- **Hạn chế:** chưa có API public, UI đơn giản, chưa realtime, chưa đa ngôn ngữ tự động.
- **Hướng phát triển:** bổ sung DRF + JWT API, thêm frontend React/Vue, thêm notification/email, triển khai production (Gunicorn/Nginx, HTTPS), logging/monitoring, phân quyền chi tiết theo object.

## 12. Kết luận
- Django là lựa chọn phù hợp nhờ Auth/ORM/Admin tích hợp, bảo mật sẵn có và năng suất cao cho CRUD nội bộ.
- Dự án giúp nắm vững MVC (MTV), làm việc DB-first, phân quyền role-based, và quy trình SSR.
- Kiến trúc này dễ mở rộng: thêm API, frontend hiện đại, hoặc tích hợp dịch vụ thứ ba mà không phá vỡ lõi nghiệp vụ.
