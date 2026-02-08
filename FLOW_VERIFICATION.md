# Flow Verification Checklist

## ✅ Current Implementation Matches Your Flow

### Step 1: HTML Form → /submit_resume
- ✅ Form in `app/templates/index.html`
- ✅ POST endpoint: `/submit_resume/` in `app/main.py`
- ✅ Handles file upload and job description

### Step 2: Resume Evaluation Agent
- ✅ Function: `app/resume_agent.py::evaluate_resume()`
- ✅ Calls OpenAI GPT-4
- ✅ Returns structured evaluation

### Step 3: Decision Engine
- ✅ Function: `app/decision_engine.py::make_decision()`
- ✅ Rule-based logic
- ✅ Returns: SHORTLIST | REJECT | NEEDS_HUMAN_REVIEW

### Step 4: Store in DB (if NEEDS_HUMAN_REVIEW)
- ✅ Candidate saved with `status="NEEDS_HUMAN_REVIEW"`
- ✅ `final_decision = None` (waiting for human)
- ✅ Stored in database before any further action

### Step 5: Human Opens /review/{id}
- ✅ GET endpoint: `/review/{candidate_id}`
- ✅ Shows AI evaluation summary
- ✅ Displays candidate information

### Step 6: Human Submits Decision
- ✅ POST endpoint: `/review/{candidate_id}`
- ✅ Receives decision (SHORTLIST/REJECT)
- ✅ Optional comment field

### Step 7: Human Review Agent (POST)
- ✅ Saves HumanReview record
- ✅ Updates candidate.final_decision
- ✅ Updates candidate.status = "FINALIZED"
- ✅ All done in `app/main.py::submit_human_review()`

### Step 8: Email Action Agent Fires
- ✅ Function: `app/email_agent.py::trigger_email()`
- ✅ Called after human review decision
- ✅ Also called for auto-decisions (SHORTLIST/REJECT)
- ✅ Sends email notification

## Flow Logic

### For NEEDS_HUMAN_REVIEW:
1. Form → Evaluation → Decision → **Store in DB** → Redirect to `/review/{id}`
2. Human opens review page
3. Human submits decision
4. Human Review Agent processes
5. **Email Action Agent fires**

### For SHORTLIST/REJECT (Auto):
1. Form → Evaluation → Decision → **Store in DB** → **Email Action Agent fires immediately**

## Key Points

✅ **All candidates stored in DB** - No candidate is lost
✅ **Human review required** for borderline cases
✅ **Email only after decision** - Never before
✅ **Complete audit trail** - HumanReview table tracks all reviews
✅ **Proper status management** - NEEDS_HUMAN_REVIEW → FINALIZED

## Testing the Flow

1. Submit a resume that will trigger NEEDS_HUMAN_REVIEW
2. Verify candidate is stored in DB with status="NEEDS_HUMAN_REVIEW"
3. Open `/review/{candidate_id}` in browser
4. Submit a decision
5. Verify email is triggered
6. Check database for HumanReview record
