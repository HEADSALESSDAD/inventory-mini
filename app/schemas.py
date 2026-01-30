# app/schemas.py
"""
Schemas یعنی شکل داده‌هایی که API می‌گیرد و برمی‌گرداند.
Pydantic کمک می‌کند ورودی‌ها validate شوند (یعنی خراب وارد نشود).
"""

from pydantic import BaseModel, Field
from typing import Optional

class ItemCreate(BaseModel):
    # ورودی برای ساخت کالا
    name: str = Field(..., min_length=1)
    sku: Optional[str] = None
    qty: int = Field(0, ge=0)
    price: Optional[float] = Field(None, ge=0)

class ItemUpdate(BaseModel):
    # ورودی برای آپدیت (همه چیز اختیاری)
    name: Optional[str] = Field(None, min_length=1)
    sku: Optional[str] = None
    qty: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)

class ItemOut(BaseModel):
    # خروجی API
    id: int
    name: str
    sku: Optional[str]
    qty: int
    price: Optional[float]

    class Config:
        # اجازه می‌دهد از مدل SQLAlchemy مستقیم تبدیل شود
        from_attributes = True
