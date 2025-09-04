"""
Database connection and session management for SupplyChainRescue AI.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from backend.config import settings
from backend.models.sql_models import Base

# Create engine based on database URL
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)

# Session local for connection pooling
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI dependency to get database session


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Function to create all tables


def create_tables():
    Base.metadata.create_all(bind=engine)

# Function to drop tables (useful for testing)


def drop_tables():
    Base.metadata.drop_all(bind=engine)

# Optional: Function to set up initial data (seed)


def setup_initial_data():
    # This can be expanded to seed initial data
    pass
