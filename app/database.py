"""
================================================================================
DATABASE CONFIGURATION MODULE
================================================================================

This module handles database connection and session management using SQLAlchemy.

Features:
- Supports both PostgreSQL and SQLite
- Automatic fallback to SQLite if PostgreSQL is not configured
- Session management with dependency injection for FastAPI
- Base class for SQLAlchemy models

Configuration:
- DATABASE_URL: Set in .env file (optional)
  - If set: Uses PostgreSQL connection string
  - If not set: Defaults to SQLite (sqlite:///./agentic_hiring.db)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# Database URL Configuration
# ============================================================================
# Check if DATABASE_URL is set in environment variables
# If not set, default to SQLite for easy local development
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Default to SQLite for easy setup (no external database required)
    DATABASE_URL = "sqlite:///./agentic_hiring.db"
    # SQLite requires special connection arguments for thread safety
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Use PostgreSQL (Render provides this automatically)
    # Render's PostgreSQL connection string is already in the correct format
    # pool_pre_ping=True ensures connections are validated before use (important for Render)
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ============================================================================
# Session Management
# ============================================================================
# Create session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all SQLAlchemy models
# All models should inherit from this Base
Base = declarative_base()


# ============================================================================
# Database Dependency for FastAPI
# ============================================================================
def get_db():
    """
    Database session dependency for FastAPI routes.
    
    This function provides a database session that is automatically
    created for each request and closed after the request completes.
    
    Usage in FastAPI routes:
        @app.get("/example")
        def example_route(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        # Provide the session to the route handler
        yield db
    finally:
        # Always close the session after request completes
        db.close()
