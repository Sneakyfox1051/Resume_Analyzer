"""
================================================================================
EMAIL ACTION AGENT - Automated Email Sending
================================================================================

This module implements the Email Action Agent that sends email notifications
to candidates based on hiring decisions.

Flow:
1. Receives candidate ID and decision (SHORTLIST/REJECT)
2. Generates appropriate email content based on decision
3. Sends email via SMTP (Gmail, Outlook, etc.)
4. Logs email attempt in database (success or failure)

Email Types:
- SHORTLIST: Interview invitation email
- REJECT: Rejection notification email
- Other: Generic action required email

Configuration (in .env file):
- SMTP_SERVER: SMTP server address (e.g., smtp.gmail.com)
- SMTP_PORT: SMTP port (usually 587 for TLS)
- SMTP_USER: Email address for authentication
- SMTP_PASS: Email password or app password

Note: Email sending is optional. If SMTP credentials are not configured,
the agent will skip sending but log a warning.
"""

import os
import smtplib
from email.mime.text import MIMEText
from app.models import Candidate, EmailLog
from app.database import get_db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# SMTP Configuration from Environment Variables
# ============================================================================
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


# ============================================================================
# Email Content Generation
# ============================================================================
def generate_email_content(candidate: Candidate, decision: str):
    """
    Generate email subject and body based on decision type.
    
    Args:
        candidate: Candidate object (for potential personalization)
        decision: Decision string (SHORTLIST, REJECT, etc.)
    
    Returns:
        tuple: (subject, body) strings for the email
    """
    if decision == "SHORTLIST":
        subject = f"Interview Invitation – Role"
        body = f"""Hi Candidate,

You are shortlisted for the role. Please reply to schedule an interview.

Regards,
HR Team"""
    elif decision == "REJECT":
        subject = "Application Status – Rejected"
        body = """Hi Candidate,

Thank you for applying. Unfortunately, you are not selected at this time.

Regards,
HR Team"""
    else:
        subject = "Action Required"
        body = """Hi Candidate,

We need additional information. Please reply with the requested details.

Regards,
HR Team"""
    
    return subject, body


# ============================================================================
# Email Action Agent - Main Function
# ============================================================================
def trigger_email(candidate_id: int, decision: str):
    """
    Send email notification to candidate based on decision.
    
    This is the Email Action Agent that:
    1. Checks if SMTP is configured
    2. Fetches candidate from database
    3. Generates email content
    4. Sends email via SMTP
    5. Logs email attempt in database
    
    Called in two scenarios:
    - After automated decision (SHORTLIST/REJECT from Decision Engine)
    - After human review decision (SHORTLIST/REJECT from Human Review Agent)
    
    Args:
        candidate_id: ID of the candidate to send email about
        decision: Decision string (SHORTLIST, REJECT, etc.)
    """
    # ========================================================================
    # Check SMTP Configuration
    # ========================================================================
    # Email sending is optional - skip if credentials not configured
    if not SMTP_USER or not SMTP_PASS:
        print("⚠️  Email Action Agent: SMTP credentials not configured in .env file")
        print("   To enable emails, add SMTP_USER and SMTP_PASS to your .env file")
        return
    
    print(f"📧 Email Action Agent: Sending {decision} email to candidate {candidate_id}...")
    
    # ========================================================================
    # Fetch Candidate from Database
    # ========================================================================
    db = next(get_db())
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        print(f"❌ Candidate {candidate_id} not found in database")
        return
    
    # ========================================================================
    # Generate Email Content
    # ========================================================================
    subject, body = generate_email_content(candidate, decision)
    
    # ========================================================================
    # Create Email Message
    # ========================================================================
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = "adabbawa06@gmail.com"  # Candidate email address
    
    # ========================================================================
    # Send Email via SMTP
    # ========================================================================
    try:
        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            # Enable TLS encryption
            server.starttls()
            
            # Authenticate with email credentials
            server.login(SMTP_USER, SMTP_PASS)
            
            # Send email
            server.sendmail(SMTP_USER, [msg['To']], msg.as_string())
        
        # ====================================================================
        # Log Successful Email
        # ====================================================================
        email_log = EmailLog(
            candidate_id=candidate.id,
            email_type=decision,
            status="SENT"
        )
        db.add(email_log)
        db.commit()
        
        print(f"✅ Email sent successfully for candidate {candidate_id}")
        
    except Exception as e:
        # ====================================================================
        # Log Failed Email
        # ====================================================================
        print(f"❌ Email send failed: {e}")
        email_log = EmailLog(
            candidate_id=candidate.id,
            email_type=decision,
            status="FAILED"
        )
        db.add(email_log)
        db.commit()
