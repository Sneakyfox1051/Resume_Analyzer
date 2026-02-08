"""
================================================================================
DATABASE INITIALIZATION SCRIPT
================================================================================

This script creates all database tables defined in the models.

Usage:
    python init_db.py

What it does:
1. Imports all SQLAlchemy models (Candidate, HumanReview, EmailLog)
2. Creates all tables in the database using Base.metadata.create_all()
3. Uses the database engine configured in app.database

Note:
- Safe to run multiple times (won't recreate existing tables)
- Run this once after setting up the project
- If using SQLite, creates agentic_hiring.db file
- If using PostgreSQL, creates tables in the configured database
"""

from app.database import engine, Base
from app.models import Candidate, HumanReview, EmailLog

if __name__ == "__main__":
    print("🔄 Creating database tables...")
    
    # Create all tables defined in models
    # This uses SQLAlchemy's declarative base to automatically create
    # tables for all models that inherit from Base
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully!")
    print("   Tables created:")
    print("   - candidates")
    print("   - human_reviews")
    print("   - email_logs")
