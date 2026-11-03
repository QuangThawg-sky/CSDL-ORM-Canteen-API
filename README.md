\# Canteen API — PostgreSQL và SQLAlchemy



\## 1. Giới thiệu



Dự án chuyển API quản lý căng tin sang PostgreSQL, sử dụng SQLAlchemy ORM để thao tác dữ liệu và Alembic để quản lý migration.



\## 2. Công nghệ



\- Python

\- FastAPI

\- PostgreSQL 16

\- SQLAlchemy

\- Alembic

\- Docker Compose



\## 3. Cấu trúc dự án



\- `app/`: mã nguồn API, models, schemas, kết nối database và seed dữ liệu.

\- `migrations/`: các migration của Alembic.

\- `docker-compose.yml`: cấu hình PostgreSQL.

\- `.env.example`: mẫu cấu hình môi trường.



\## 4. Cài đặt và chạy



Tạo môi trường ảo và cài đặt các thư viện cần thiết:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

pip install fastapi "uvicorn\[standard]" sqlalchemy "psycopg\[binary]" alembic python-dotenv

```



Tạo file `.env` dựa trên `.env.example`, với cấu hình kết nối PostgreSQL phù hợp.



Khởi động PostgreSQL:



```powershell

docker compose up -d

```



Chạy migration:



```powershell

alembic upgrade head

```



Thêm dữ liệu mẫu:



```powershell

python -m app.seed

```



Khởi động API:



```powershell

python -m uvicorn app.main:app --reload

```



Mở Swagger tại http://127.0.0.1:8000/docs



\## 5. Các API chính



| Phương thức | Endpoint | Chức năng |

|---|---|---|

| GET | `/categories` | Danh sách danh mục |

| POST | `/categories` | Tạo danh mục |

| GET | `/menu-items` | Danh sách món ăn, lọc và sắp xếp |

| GET | `/menu-items/{item\_id}` | Chi tiết món ăn |

| POST | `/menu-items` | Tạo món ăn |

| PUT/PATCH | `/menu-items/{item\_id}` | Cập nhật món ăn |

| DELETE | `/menu-items/{item\_id}` | Xóa món ăn |

| POST | `/orders` | Tạo đơn hàng |

| GET | `/orders/{order\_id}` | Chi tiết đơn hàng |



\## 6. Cơ sở dữ liệu và giao dịch



Cơ sở dữ liệu gồm các bảng `categories`, `menu\_items`, `orders` và `order\_items`.



Đơn hàng lưu giá tại thời điểm đặt hàng (`unit\_price`) và tính thành tiền theo số lượng. API cần bảo đảm tính toàn vẹn dữ liệu khi đặt hàng, không cho đặt món không khả dụng và xử lý các trường hợp dữ liệu không hợp lệ.



\## 7. Migration



Áp dụng toàn bộ migration:



```powershell

alembic upgrade head

```



Hạ một phiên bản migration:



```powershell

alembic downgrade -1

```



\## 8. Bảo mật



Không commit file `.env` hoặc thông tin bí mật lên GitHub. Sử dụng `.env.example` làm mẫu cấu hình.



\## 9. Bằng chứng thực hiện



Các ảnh minh chứng được lưu trong thư mục `docs/` khi hoàn thành, gồm ảnh dữ liệu còn tồn tại sau khi khởi động lại dịch vụ, kết quả truy vấn SQL và sơ đồ ERD.



