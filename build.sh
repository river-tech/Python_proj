#!/usr/bin/env bash
# Dừng script ngay lập tức nếu có lỗi xảy ra
set -euo pipefail

echo "==> Cài đặt các thư viện phụ thuộc..."
pip install -r requirements.txt

echo "==> Gom các file tĩnh (CSS, JS, Images)..."
# Bắt buộc phải có khi dùng Whitenoise trên production
python manage.py collectstatic --no-input

echo "==> Cập nhật cấu trúc database..."
# Khởi tạo các bảng hệ thống của Django (Auth, Sessions...)
python manage.py migrate

echo "==> Chạy script tạo dữ liệu mẫu (Seed)..."
# Chỉ nên chạy nếu script seed của bạn có cơ chế kiểm tra (if not exists)
# để tránh lỗi duplicate data mỗi lần deploy lại code.
python seed_vbafi_users.py

echo "==> Quá trình Build hoàn tất!"