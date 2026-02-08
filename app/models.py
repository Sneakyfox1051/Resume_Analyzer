"""
================================================================================
DATABASE MODELS - SQLAlchemy ORM Models
================================================================================

This module defines all database models (tables) using SQLAlchemy ORM.

Models:
1. Candidate - Stores resume submissions and evaluation results
2. HumanReview - Tracks human reviewer decisions and comments
3. EmailLog - Logs all email sending attempts and their status

All models inherit from Base (defined in app.database) and use SQLAlchemy's
declarative base for automatic table creation.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


# ============================================================================
# MODEL 1: Candidate
# ============================================================================
class Candidate(Base):
    """
    Represents a candidate who has submitted a resume.
    
    Stores:
    - Resume text and job description
    - Evaluation results from Resume Evaluation Agent
    - Agent decision (SHORTLIST/REJECT/NEEDS_HUMAN_REVIEW)
    - Final decision (after human review if needed)
    - Status tracking (RECEIVED/NEEDS_HUMAN_REVIEW/FINALIZED)
    - Timestamps for audit trail
    
    Relationships:
    - One-to-many with HumanReview (a candidate can have multiple reviews)
    - One-to-many with EmailLog (multiple emails can be sent per candidate)
    """
    __tablename__ = "candidates"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Resume and job description data
    resume_text = Column(String, nullable=False)  # Extracted text from PDF
    job_description = Column(String, nullable=False)  # Job description from form
    
    # Evaluation results from Resume Evaluation Agent
    agent_score = Column(Float)  # Overall score (if calculated)
    agent_decision = Column(String)  # SHORTLIST, REJECT, or NEEDS_HUMAN_REVIEW
    evaluation_output = Column(JSON)  # Full evaluation JSON from OpenAI
    
    # Final decision and status
    final_decision = Column(String)  # Final decision after human review (if needed)
    status = Column(String, default="RECEIVED")  # RECEIVED, NEEDS_HUMAN_REVIEW, FINALIZED
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============================================================================
# MODEL 2: HumanReview
# ============================================================================
class HumanReview(Base):
    """
    Tracks human reviewer decisions and comments.
    
    Created when a human reviewer makes a decision on a candidate that
    was flagged as NEEDS_HUMAN_REVIEW by the Decision Engine.
    
    Stores:
    - Reviewer identifier
    - Decision (SHORTLIST or REJECT)
    - Optional comment/notes from reviewer
    - Timestamp of review
    """
    __tablename__ = "human_reviews"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to Candidate
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    
    # Review data
    reviewer = Column(String)  # Reviewer identifier (e.g., "HR_USER")
    decision = Column(String)  # SHORTLIST or REJECT
    comment = Column(String)  # Optional comment from reviewer
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# MODEL 3: EmailLog
# ============================================================================
class EmailLog(Base):
    """
    Logs all email sending attempts for audit and debugging.
    
    Created every time the Email Action Agent attempts to send an email,
    whether successful or not.
    
    Stores:
    - Candidate ID (who the email was about)
    - Email type (SHORTLIST, REJECT, etc.)
    - Status (SENT or FAILED)
    - Timestamp of send attempt
    """
    __tablename__ = "email_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to Candidate
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    
    # Email data
    email_type = Column(String)  # SHORTLIST, REJECT, etc.
    status = Column(String)  # SENT or FAILED
    
    # Timestamp
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
