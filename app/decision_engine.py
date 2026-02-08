"""
================================================================================
DECISION ENGINE - Automated Decision Making
================================================================================

This module implements the rule-based Decision Engine that makes automated
decisions based on evaluation scores from the Resume Evaluation Agent.

Decision Logic:
1. SHORTLIST: High confidence (>= 0.8) AND high skills match (>= 0.75)
2. REJECT: Low confidence (<= 0.4)
3. NEEDS_HUMAN_REVIEW: Everything else (medium confidence, edge cases)

The Decision Engine acts as a filter:
- Clear-cut cases → Automated decision (SHORTLIST or REJECT)
- Ambiguous cases → Flag for human review

This ensures:
- Fast processing for obvious candidates
- Human judgment for borderline cases
- Consistent decision criteria
"""


# ============================================================================
# Decision Making Function
# ============================================================================
def make_decision(evaluation_output: dict):
    """
    Make automated decision based on evaluation scores.
    
    Decision Rules:
    - SHORTLIST: High confidence (>= 0.8) AND high skills match (>= 0.75)
      → Strong candidate, automatically shortlist
    - REJECT: Low confidence (<= 0.4)
      → Weak candidate, automatically reject
    - NEEDS_HUMAN_REVIEW: Everything else
      → Borderline case, requires human judgment
    
    Args:
        evaluation_output: Dictionary from Resume Evaluation Agent containing:
            - confidence: float (0-1)
            - skills_match: float (0-1)
            - Other evaluation metrics
    
    Returns:
        str: Decision string - "SHORTLIST", "REJECT", or "NEEDS_HUMAN_REVIEW"
    """
    # Extract key metrics from evaluation
    confidence = evaluation_output.get("confidence", 0)
    skills_match = evaluation_output.get("skills_match", 0)
    
    # ========================================================================
    # Rule 1: SHORTLIST - High confidence and strong skills match
    # ========================================================================
    # Automatically shortlist candidates with:
    # - High confidence (>= 0.8) - Agent is confident in evaluation
    # - Strong skills match (>= 0.75) - Skills align well with job
    if confidence >= 0.8 and skills_match >= 0.75:
        return "SHORTLIST"
    
    # ========================================================================
    # Rule 2: REJECT - Low confidence
    # ========================================================================
    # Automatically reject candidates with:
    # - Low confidence (<= 0.4) - Agent is not confident, likely poor match
    elif confidence <= 0.4:
        return "REJECT"
    
    # ========================================================================
    # Rule 3: NEEDS_HUMAN_REVIEW - Borderline cases
    # ========================================================================
    # Flag for human review when:
    # - Medium confidence (0.4 < confidence < 0.8)
    # - Or skills match is moderate (0.5 < skills_match < 0.75)
    # - Or any other edge case
    # Human judgment is needed to make the final decision
    else:
        return "NEEDS_HUMAN_REVIEW"
