# app/models.py
"""
Database tables (SQLAlchemy Models)

Beginner notes:
- Each class = a table
- Each column = a field in that table
"""

from __future__ import annotations

from sqlalchemy import Column, Integer, String, Numeric
from .db import Base


class Item(Base):
    __tablename__ = "items"

    # Primary key (auto increment)
    id = Column(Integer, primary_key=True, index=True)

    # Basic fields
    name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=False, index=True)

    # qty = quantity in stock (integer)
    qty = Column(Integer, nullable=False, default=0)

    # price = optional (Decimal money)
    price = Column(Numeric(10, 2), nullable=True)

