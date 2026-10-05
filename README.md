# 🛒 E-Commerce Data Engineering Pipeline (PostgreSQL)

Dự án Data Engineering xây dựng hệ cơ sở dữ liệu mẫu cho hệ thống Thương mại Điện tử (E-Commerce) trên **PostgreSQL**, kết hợp cùng Python và **Faker** để sinh dữ liệu giả lập (mock data) quy mô lớn với tính toàn vẹn quan hệ và các ràng buộc nghiệp vụ (Constraints).

---

## 📌 Tính năng nổi bật

- **Kiến trúc phân tầng gọn gàng**:
  - `variable.py`: Tập trung quản lý toàn bộ câu truy vấn SQL (DDL, DML), lệnh dọn dẹp (`TRUNCATE`) và dữ liệu danh mục tĩnh.
  - `create_table.py`: Thực thi tạo bảng tự động, code tối giản chỉ ~20 dòng.
  - `insert_value.py`: Script sinh và nạp dữ liệu tự động với cơ chế nạp theo lô (`batch insert`), reset ID (`RESTART IDENTITY CASCADE`) chống duplicate và tối ưu hiệu năng.
- **Mô hình hóa dữ liệu quan hệ chặt chẽ**:
  - Danh mục đa cấp cha - con (`Category Level 1` & `Level 2`).
  - Sản phẩm (`Product`) liên kết đa chiều với Thương hiệu (`Brand`), Người bán (`Seller`) và Danh mục (`Category`).
  - Chương trình khuyến mãi (`Promotion`) và liên kết sản phẩm (`Promotion Product`) với các ràng buộc về ngày bắt đầu/kết thúc và hạn mức giảm giá.
  - Thiết kế sẵn sàng cho bảng Đơn hàng (`Orders`) và Chi tiết đơn hàng (`Order Item`) quy mô hàng triệu bản ghi.

---

## 🗂️ Cấu trúc Thư mục

```text
Project3/
├── config.py             # Module đọc cấu hình kết nối database từ file database.ni
├── config_engine.py      # Module tạo SQLAlchemy Engine kết nối PostgreSQL
├── connect.py            # Kiểm tra trạng thái kết nối tới PostgreSQL
├── create_table.py       # Script tạo cấu trúc toàn bộ bảng (DDL)
├── insert_value.py       # Script sinh và nạp dữ liệu bằng Psycopg2 thuần
├── insert_value_pandas.py# Script sinh và nạp dữ liệu bằng Pandas + SQLAlchemy
├── variable.py           # Quản lý tập trung SQL queries, DDL, DML và dữ liệu cố định
├── ecommerce.sql         # Bộ câu truy vấn SQL kiểm tra, xác thực số lượng dữ liệu
├── pyproject.toml        # Cấu hình dự án và dependencies (quản lý bằng uv)
├── uv.lock               # Khóa chính xác phiên bản các gói phụ thuộc
└── README.md             # Tài liệu hướng dẫn dự án
```

---

## 📊 Mô hình Dữ liệu (Database Schema)

| Tên bảng | Số lượng bản ghi mẫu | Mô tả |
| :--- | :---: | :--- |
| **`brand`** | 20 | Thương hiệu hàng hóa, tên unique |
| **`category`** | 25 | 5 danh mục chính (Level 1) & 20 danh mục con (Level 2) |
| **`seller`** | 50 | Nhà bán lẻ (Official, Marketplace) tại Việt Nam |
| **`customer`** | 30,000 | Khách hàng với email và phone unique (chuẩn VN), nạp theo batch 5,000 |
| **`product`** | 3,000 | Sản phẩm liên kết Category, Brand, Seller kèm SKU unique |
| **`promotion`** | 30 | Chiến dịch khuyến mãi (percentage, fixed_amount) |
| **`promotion_product`**| 500 | Liên kết Promo - Product, trung bình 15-18 sản phẩm / promo |
| **`orders`** | *Đang phát triển* | Đơn hàng mua sắm theo trạng thái |
| **`order_item`** | *Đang phát triển* | Chi tiết từng mặt hàng trong đơn |

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

Dự án sử dụng **[uv](https://docs.astral.sh/uv/)** — công cụ quản lý package và virtual environment bằng Rust siêu tốc.

### 1. Đồng bộ môi trường và thư viện với `uv`

Chỉ cần một lệnh duy nhất, `uv` sẽ tự động tạo virtual environment và cài đặt toàn bộ dependencies trong nháy mắt:

```bash
uv sync
```

### 2. Cấu hình kết nối PostgreSQL

Tạo file `database.ni` tại thư mục gốc của dự án với nội dung:

```ini
[postgresql]
host=localhost
database=your_database_name
user=postgres
password=your_password
port=5432
```

### 3. Kiểm tra kết nối

```bash
uv run python connect.py
# hoặc kiểm tra engine SQLAlchemy:
uv run python config_engine.py
```

### 4. Tạo bảng trong Database

```bash
uv run python create_table.py
```

### 5. Nạp dữ liệu giả lập (Data Ingestion)

Bạn có thể lựa chọn 1 trong 2 phiên bản để chạy:

- **Cách 1: Nạp bằng Psycopg2 thuần (Tối ưu hiệu năng SQL):**
  ```bash
  uv run python insert_value.py
  ```

- **Cách 2: Nạp bằng Pandas + SQLAlchemy (DataFrame pipeline):**
  ```bash
  uv run python insert_value_pandas.py
  ```

> **Lưu ý**: Cả 2 script đều đã tích hợp hàm `truncate_all_tables()`. Mỗi lần chạy, hệ thống sẽ tự động làm sạch dữ liệu cũ và reset ID tự tăng (`RESTART IDENTITY CASCADE`) về 1, đảm bảo không bao giờ bị lỗi trùng lặp dữ liệu (`duplicate key`).

---

## 🔍 Kiểm tra Dữ liệu

Sau khi nạp xong, bạn có thể mở **pgAdmin 4** (hoặc `psql`) và chạy file `ecommerce.sql` hoặc câu truy vấn sau:

```sql
SELECT 'brand' AS table_name, COUNT(*) AS total_rows FROM brand
UNION ALL
SELECT 'category', COUNT(*) FROM category
UNION ALL
SELECT 'seller', COUNT(*) FROM seller
UNION ALL
SELECT 'customer', COUNT(*) FROM customer
UNION ALL
SELECT 'product', COUNT(*) FROM product
UNION ALL
SELECT 'promotion', COUNT(*) FROM promotion
UNION ALL
SELECT 'promotion_product', COUNT(*) FROM promotion_product;
```
