# app/schemas.py
"""
API schemas (Pydantic)

Beginner notes:
- These classes describe what the API receives/sends
- They are NOT database tables, just "data shapes"
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(..., examples=["Oil Filter"])
    sku: str = Field(..., examples=["TOY-OF-90915"])
    qty: int = Field(0, ge=0, examples=[10])
    price: Optional[float] = Field(None, ge=0, examples=[12.50])


class ItemCreate(ItemBase):
    """Used when creating a new item."""
    pass


class ItemUpdate(BaseModel):
    """Used when updating an existing item (all fields optional)."""
    name: Optional[str] = None
    sku: Optional[str] = None
    qty: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)


class ItemOut(ItemBase):
    """What we return to clients (includes ID)."""
    id: int

    # Pydantic v2: allow reading from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)
