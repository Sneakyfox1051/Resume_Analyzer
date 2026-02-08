"""
================================================================================
MAIN APPLICATION FILE - FastAPI Entry Point
================================================================================

This is the core application file that orchestrates the entire agentic hiring
pipeline. It defines all API routes and manages the flow:

Flow Overview:
1. HTML Form → User submits resume + job description
2. Resume Evaluation Agent → Analyzes resume using OpenAI
3. Decision Engine → Makes automated decision (SHORTLIST/REJECT/NEEDS_HUMAN_REVIEW)
4. Database Storage → Saves candidate information
5. Conditional Branch:
   - If NEEDS_HUMAN_REVIEW → Redirect to human review page
   - If SHORTLIST/REJECT → Send email immediately
6. Human Review (if needed) → Human makes final decision
7. Email Action Agent → Sends email notification

Routes:
- GET  /                    → Main form page
- POST /submit_resume/      → Submit resume for evaluation
- GET  /review/{id}         → Human review page
- POST /review/{id}         → Submit human review decision
- GET  /candidates          → View all candidates dashboard
- GET  /candidate/{id}      → View candidate details
"""

import os
from pathlib import Path
from fastapi import FastAPI, Depends, Request, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

# Import database and models
from app.database import get_db
from app.models import Candidate, HumanReview

# Import agent modules
from app.utils import extract_text_from_pdf, extract_text_with_ocr, clean_resume_text
from app.resume_agent import evaluate_resume
from app.decision_engine import make_decision
from app.email_agent import trigger_email

# ============================================================================
# FastAPI Application Initialization
# ============================================================================
app = FastAPI(title="Agentic Hiring Pipeline")

# Configure template directory for HTML rendering
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ============================================================================
# ROUTE 1: Main Form Page (GET /)
# ============================================================================
@app.get("/")
def read_form(request: Request):
    """
    Display the main HTML form for resume submission.
    
    This is the entry point where users can:
    - Upload a PDF resume
    - Enter a job description
    - Submit for evaluation
    
    Query Parameters:
    - success: Optional success message to display
    - error: Optional error message to display
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "success": request.query_params.get("success"),
            "error": request.query_params.get("error")
        }
    )


# ============================================================================
# ROUTE 2: Submit Resume (POST /submit_resume/)
# ============================================================================
# This route implements Steps 1-4 of the pipeline:
# Step 1: File upload and validation
# Step 2: Resume text extraction (PDF → OCR fallback)
# Step 2.5: Resume Evaluation Agent (calls OpenAI)
# Step 3: Decision Engine (automated decision)
# Step 4: Database storage
@app.post("/submit_resume/")
async def submit_resume(
    request: Request,
    job_description: str = Form(...),
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Process resume submission through the agentic pipeline.
    
    Flow:
    1. Validate PDF file type
    2. Extract text from PDF (with OCR fallback for scanned PDFs)
    3. Clean and normalize resume text
    4. Run Resume Evaluation Agent (OpenAI analysis)
    5. Run Decision Engine (automated decision)
    6. Store candidate in database
    7. Branch based on decision:
       - NEEDS_HUMAN_REVIEW → Redirect to review page
       - SHORTLIST/REJECT → Send email and redirect to home
    
    Args:
        request: FastAPI request object
        job_description: Job description text from form
        resume_file: Uploaded PDF file
        db: Database session
    
    Returns:
        RedirectResponse to either review page or home page with message
    """
    # ========================================================================
    # STEP 1: File Validation
    # ========================================================================
    if resume_file.content_type != "application/pdf":
        return RedirectResponse(
            url="/?error=Only+PDF+files+are+allowed.",
            status_code=303
        )
    
    # ========================================================================
    # STEP 2: Resume Text Extraction (Smart Extraction with OCR Fallback)
    # ========================================================================
    print("🔄 Step 2: Extracting text from resume...")
    
    # Read file bytes once (needed for both PDF extraction and OCR)
    file_bytes = await resume_file.read()
    
    # Try normal PDF text extraction first (faster, works for text-based PDFs)
    from io import BytesIO
    file_obj = BytesIO(file_bytes)
    text = extract_text_from_pdf(file_obj)
    
    # Decision point: If extracted text is too short, likely a scanned PDF
    # Fall back to OCR (Optical Character Recognition) for image-based PDFs
    if len(text) < 300:
        print("   Low text detected → Using OCR for scanned PDF...")
        text = extract_text_with_ocr(file_bytes)
    
    # Clean and normalize the extracted text
    resume_text = clean_resume_text(text)
    print(f"   Extracted {len(resume_text)} characters from resume")
    
    # ========================================================================
    # STEP 2.5: Resume Evaluation Agent
    # ========================================================================
    # This agent uses OpenAI GPT-4 to analyze the resume against the job description
    # Returns structured evaluation with scores, skills match, confidence, etc.
    print("🔄 Step 2.5: Running Resume Evaluation Agent (OpenAI)...")
    evaluation_output = evaluate_resume(resume_text, job_description)
    
    if not evaluation_output:
        return RedirectResponse(
            url="/?error=Resume+evaluation+failed.+Please+check+your+OpenAI+API+key+and+try+again.",
            status_code=303
        )
    
    print(f"   Evaluation complete - Confidence: {evaluation_output.get('confidence', 'N/A')}")
    
    # ========================================================================
    # STEP 3: Decision Engine
    # ========================================================================
    # Rule-based decision engine that makes automated decisions based on
    # evaluation scores. Returns: SHORTLIST, REJECT, or NEEDS_HUMAN_REVIEW
    print("🔄 Step 3: Running Decision Engine...")
    agent_decision = make_decision(evaluation_output)
    print(f"   Decision: {agent_decision}")
    
    # ========================================================================
    # STEP 4: Store Candidate in Database
    # ========================================================================
    # Save all candidate information including resume text, job description,
    # evaluation output, and decision status
    print("🔄 Step 4: Storing candidate in database...")
    candidate = Candidate(
        resume_text=resume_text,
        job_description=job_description,
        agent_decision=agent_decision,
        evaluation_output=evaluation_output,
        status="NEEDS_HUMAN_REVIEW" if agent_decision == "NEEDS_HUMAN_REVIEW" else "FINALIZED",
        final_decision=agent_decision if agent_decision != "NEEDS_HUMAN_REVIEW" else None
    )
    
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    print(f"   Candidate ID: {candidate.id} saved with status: {candidate.status}")
    
    # ========================================================================
    # FLOW BRANCH: Auto Decision vs Human Review
    # ========================================================================
    if agent_decision == "NEEDS_HUMAN_REVIEW":
        # ====================================================================
        # BRANCH A: Needs Human Review → Redirect to Review Page
        # ====================================================================
        # The decision engine determined that human judgment is needed.
        # Redirect to the human review page where a reviewer can make the
        # final decision (SHORTLIST or REJECT)
        print("   → Redirecting to human review page...")
        return RedirectResponse(url=f"/review/{candidate.id}", status_code=303)
    else:
        # ====================================================================
        # BRANCH B: Auto Decision (SHORTLIST/REJECT) → Send Email Immediately
        # ====================================================================
        # The decision engine made a confident decision. Send email notification
        # immediately without human intervention.
        print(f"   → Auto decision ({agent_decision}), sending email...")
        trigger_email(candidate.id, agent_decision)
        decision_msg = "shortlisted" if agent_decision == "SHORTLIST" else "rejected"
        return RedirectResponse(
            url=f"/?success=Candidate+{decision_msg}+successfully.+Email+sent.",
            status_code=303
        )


# ============================================================================
# ROUTE 3: Human Review Page (GET /review/{candidate_id})
# ============================================================================
# STEP 5: Human Opens Review Page
# This is where a human reviewer can see the candidate's evaluation and
# make a final decision
@app.get("/review/{candidate_id}")
def review_page(
    candidate_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Display the human review page for a candidate that needs human judgment.
    
    This page shows:
    - Candidate evaluation summary
    - Skills match scores
    - Agent's recommendation
    - Form to submit final decision (SHORTLIST or REJECT)
    
    Args:
        candidate_id: ID of the candidate to review
        request: FastAPI request object
        db: Database session
    
    Returns:
        TemplateResponse with review page HTML
    """
    # Fetch candidate from database - only show candidates pending review
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.status == "NEEDS_HUMAN_REVIEW"
    ).first()
    
    if not candidate:
        return RedirectResponse(
            url="/?error=Candidate+not+found+or+not+pending+review.",
            status_code=303
        )
    
    # Extract evaluation data for display
    eval_output = candidate.evaluation_output or {}
    summary = eval_output.get("summary", "No summary available.")
    
    # Format summary for display
    if isinstance(summary, str):
        formatted_summary = summary
    else:
        formatted_summary = str(summary)
    
    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "candidate_id": candidate.id,
            "summary": formatted_summary,
            "evaluation": eval_output
        }
    )


# ============================================================================
# ROUTE 4: Submit Human Review (POST /review/{candidate_id})
# ============================================================================
# STEP 6 & 7: Human Submits Decision → Human Review Agent
# This endpoint processes the human reviewer's decision and triggers the
# email action agent
@app.post("/review/{candidate_id}")
def submit_human_review(
    candidate_id: int,
    decision: str = Form(...),
    comment: str = Form(""),
    db: Session = Depends(get_db)
):
    """
    Process human reviewer's decision and complete the pipeline.
    
    Flow:
    1. Validate candidate exists and is pending review
    2. Save human review decision to database
    3. Update candidate status to FINALIZED
    4. Trigger Email Action Agent to send notification
    
    Args:
        candidate_id: ID of the candidate being reviewed
        decision: Final decision (SHORTLIST or REJECT)
        comment: Optional comment from reviewer
        db: Database session
    
    Returns:
        RedirectResponse to home page with success message
    """
    print(f"🔄 Step 6: Human submitted decision for candidate {candidate_id}")
    print(f"   Decision: {decision}")
    
    # Fetch candidate - must be in NEEDS_HUMAN_REVIEW status
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id,
        Candidate.status == "NEEDS_HUMAN_REVIEW"
    ).first()
    
    if not candidate:
        return RedirectResponse(
            url="/?error=Candidate+not+found+or+already+finalized.",
            status_code=303
        )
    
    # ========================================================================
    # STEP 7: Human Review Agent - Save Review & Update Status
    # ========================================================================
    # Save the human reviewer's decision and update candidate status
    print("🔄 Step 7: Human Review Agent processing...")
    
    # Update candidate with final decision
    candidate.final_decision = decision
    candidate.status = "FINALIZED"
    
    # Create review record for audit trail
    review = HumanReview(
        candidate_id=candidate.id,
        reviewer="HR_USER",
        decision=decision,
        comment=comment
    )
    
    db.add(review)
    db.commit()
    print(f"   Review saved, candidate status updated to FINALIZED")
    
    # ========================================================================
    # STEP 8: Email Action Agent - Trigger Email
    # ========================================================================
    # Send email notification based on the final decision
    print("🔄 Step 8: Email Action Agent firing...")
    trigger_email(candidate.id, decision)
    
    # Redirect back to home with success message
    decision_msg = "shortlisted" if decision == "SHORTLIST" else "rejected"
    return RedirectResponse(
        url=f"/?success=Review+completed.+Candidate+{decision_msg}+and+email+sent.",
        status_code=303
    )


# ============================================================================
# ROUTE 5: Candidates Dashboard (GET /candidates)
# ============================================================================
@app.get("/candidates")
def list_candidates(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Display dashboard showing all candidates in the system.
    
    Shows:
    - Total candidates count
    - Pending review count
    - Finalized count
    - List of all candidates with their status and decisions
    
    Args:
        request: FastAPI request object
        db: Database session
    
    Returns:
        TemplateResponse with candidates dashboard HTML
    """
    # Fetch all candidates, ordered by most recent first
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    
    # Calculate statistics
    total_candidates = len(candidates)
    pending_review = len([c for c in candidates if c.status == "NEEDS_HUMAN_REVIEW"])
    finalized = len([c for c in candidates if c.status == "FINALIZED"])
    
    return templates.TemplateResponse(
        "candidates.html",
        {
            "request": request,
            "candidates": candidates,
            "total_candidates": total_candidates,
            "pending_review": pending_review,
            "finalized": finalized
        }
    )


# ============================================================================
# ROUTE 6: Candidate Detail View (GET /candidate/{candidate_id})
# ============================================================================
@app.get("/candidate/{candidate_id}")
def candidate_detail(
    candidate_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Display detailed information about a specific candidate.
    
    Shows:
    - Full resume text
    - Job description
    - Evaluation scores and summary
    - Agent decision
    - Final decision (if finalized)
    - Status and timestamps
    
    Args:
        candidate_id: ID of the candidate to view
        request: FastAPI request object
        db: Database session
    
    Returns:
        TemplateResponse with candidate detail HTML
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        return RedirectResponse(
            url="/?error=Candidate+not+found.",
            status_code=303
        )
    
    # Extract evaluation data for display
    evaluation = candidate.evaluation_output or {}
    
    return templates.TemplateResponse(
        "candidate_detail.html",
        {
            "request": request,
            "candidate": candidate,
            "evaluation": evaluation
        }
    )
