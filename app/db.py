# app/db.py
"""
Database setup (SQLAlchemy)

Beginner notes:
- engine: the "connection" to the database
- SessionLocal: creates a DB session for each request
- Base: parent class for our models (tables)

We support:
1) SQLite (simple local file) for development
2) DATABASE_URL env var for production (e.g., Postgres on hosting)
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ✅ Where to store SQLite file (project root /inventory.db)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = PROJECT_ROOT / "inventory.db"

# ✅ If hosting provides DATABASE_URL, use it. Otherwise use SQLite.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_PATH.as_posix()}")

# ✅ SQLite needs this special flag because it is file-based
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# ✅ Session factory (each request gets its own session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Base class for all tables
Base = declarative_base()
