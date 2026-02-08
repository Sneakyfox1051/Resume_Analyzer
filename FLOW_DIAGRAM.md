# HR Automation Pipeline - Flow Diagram

## Complete Flow Implementation

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. HTML Form (index.html)                                       │
│    User submits: Job Description + PDF Resume                  │
│    POST → /submit_resume/                                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Resume Evaluation Agent (app/resume_agent.py)                │
│    - Extract text from PDF (with OCR fallback)                  │
│    - Call OpenAI GPT-4 to analyze resume                        │
│    - Returns: skills_match, experience_years, domain_relevance,  │
│               red_flags, confidence, summary                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Decision Engine (app/decision_engine.py)                      │
│    Rules:                                                       │
│    - SHORTLIST: confidence ≥ 0.8 AND skills_match ≥ 0.75       │
│    - REJECT: confidence ≤ 0.4                                    │
│    - NEEDS_HUMAN_REVIEW: All other cases                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
    ┌───────────────────┐    ┌──────────────────────────────┐
    │ SHORTLIST/REJECT  │    │ NEEDS_HUMAN_REVIEW           │
    │ (Auto Decision)   │    │                              │
    └─────────┬─────────┘    └──────────────┬───────────────┘
              │                             │
              │                             ▼
              │              ┌──────────────────────────────┐
              │              │ 4. Store in Database         │
              │              │    - Candidate saved         │
              │              │    - status = NEEDS_HUMAN_REVIEW │
              │              │    - final_decision = NULL   │
              │              └──────────────┬───────────────┘
              │                             │
              │                             ▼
              │              ┌──────────────────────────────┐
              │              │ 5. Human opens /review/{id}  │
              │              │    GET /review/{candidate_id}│
              │              │    - Shows AI evaluation     │
              │              │    - Shows summary           │
              │              └──────────────┬───────────────┘
              │                             │
              │                             ▼
              │              ┌──────────────────────────────┐
              │              │ 6. Human submits decision    │
              │              │    POST /review/{candidate_id}│
              │              │    - Decision: SHORTLIST/REJECT│
              │              │    - Optional comment        │
              │              └──────────────┬───────────────┘
              │                             │
              │                             ▼
              │              ┌──────────────────────────────┐
              │              │ 7. Human Review Agent        │
              │              │    - Save HumanReview record│
              │              │    - Update candidate status│
              │              │    - Set final_decision      │
              │              └──────────────┬───────────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 8. Email Action Agent        │
              │    trigger_email()           │
              │    - Generate email content  │
              │    - Send via SMTP           │
              │    - Log email status        │
              └──────────────────────────────┘
```

## Implementation Details

### Step 1: HTML Form → /submit_resume
- **File**: `app/templates/index.html`
- **Endpoint**: `POST /submit_resume/`
- **Handler**: `app/main.py::submit_resume()`

### Step 2: Resume Evaluation Agent
- **File**: `app/resume_agent.py::evaluate_resume()`
- **Function**: Calls OpenAI GPT-4 to analyze resume
- **Returns**: Structured evaluation with scores

### Step 3: Decision Engine
- **File**: `app/decision_engine.py::make_decision()`
- **Logic**: Rule-based decision making
- **Output**: SHORTLIST | REJECT | NEEDS_HUMAN_REVIEW

### Step 4: Store in Database (if NEEDS_HUMAN_REVIEW)
- **File**: `app/main.py::submit_resume()`
- **Action**: Save candidate with status="NEEDS_HUMAN_REVIEW"
- **Database**: SQLAlchemy models in `app/models.py`

### Step 5: Human Opens Review Page
- **Endpoint**: `GET /review/{candidate_id}`
- **Handler**: `app/main.py::review_page()`
- **Template**: `app/templates/review.html`

### Step 6: Human Submits Decision
- **Endpoint**: `POST /review/{candidate_id}`
- **Handler**: `app/main.py::submit_human_review()`
- **Form Data**: decision (SHORTLIST/REJECT), comment (optional)

### Step 7: Human Review Agent
- **File**: `app/main.py::submit_human_review()`
- **Actions**:
  - Create HumanReview record
  - Update candidate.final_decision
  - Update candidate.status = "FINALIZED"

### Step 8: Email Action Agent
- **File**: `app/email_agent.py::trigger_email()`
- **Triggered**: After human review decision
- **Action**: Send email notification to candidate

## Key Points

✅ **Email fires ONLY after human review** for NEEDS_HUMAN_REVIEW cases
✅ **Email fires immediately** for auto-decisions (SHORTLIST/REJECT)
✅ **All candidates stored in DB** before any action
✅ **Human review is required** for borderline cases
✅ **Complete audit trail** via HumanReview and EmailLog tables
