# app/models.py
"""
اینجا جدول‌های دیتابیس را تعریف می‌کنیم (ORM).
ORM یعنی به جای SQL نوشتن، با کلاس‌های پایتون جدول می‌سازیم.
"""

from sqlalchemy import Column, Integer, String, Float
from .db import Base

class Item(Base):
    """
    جدول items:
    - id: کلید اصلی (عدد یکتا)
    - name: اسم کالا
    - sku: کد کالا (اختیاری)
    - qty: موجودی
    - price: قیمت (اختیاری)
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=True, index=True)
    qty = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=True)
