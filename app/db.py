# app/db.py
"""
این فایل تنظیمات دیتابیس را انجام می‌دهد.

SQLite یعنی دیتابیس یک فایل است (inventory.db)
اگر فایل وجود نداشته باشد، خودش ساخته می‌شود.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# آدرس دیتابیس (یک فایل داخل ریشه پروژه)
SQLALCHEMY_DATABASE_URL = "sqlite:///./inventory.db"

# engine = موتور ارتباط با دیتابیس
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # مخصوص SQLite
)

# SessionLocal = کارخانه ساخت Session برای هر درخواست
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base = کلاس پایه برای مدل‌ها (Table ها)
Base = declarative_base()
