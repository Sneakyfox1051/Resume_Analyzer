"""
================================================================================
RESUME EVALUATION AGENT - OpenAI Integration
================================================================================

This module implements the Resume Evaluation Agent that uses OpenAI GPT-4
to analyze resumes against job descriptions.

Flow:
1. Receives resume text and job description
2. Constructs a prompt for GPT-4
3. Calls OpenAI API to get structured evaluation
4. Returns JSON with scores, skills match, confidence, etc.

Evaluation Output Structure:
{
    "skills_match": float (0-1),      # How well skills match job requirements
    "experience_years": int,           # Years of experience
    "domain_relevance": float (0-1),   # Relevance to job domain
    "red_flags": list,                 # List of concerns/issues
    "confidence": float (0-1),         # Overall confidence in evaluation
    "summary": str                     # Human-readable summary
}

Configuration:
- OPENAI_API_KEY: Required in .env file
- Model: GPT-4 (configurable)
- Temperature: 0.1 (low for consistent results)
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import httpx

# Load environment variables from .env file
load_dotenv()


# ============================================================================
# OpenAI Client Initialization
# ============================================================================
def get_openai_client():
    """
    Initialize and return OpenAI client with proper error handling.
    
    Handles:
    - Missing API key
    - Proxy configuration issues
    - Network timeouts
    
    Returns:
        OpenAI client instance, or None if initialization fails
    """
    # Get API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OpenAI API key not found in environment variables")
        print("   Please set OPENAI_API_KEY in your .env file")
        return None
    
    try:
        # Create httpx client with timeout for better error handling
        # This prevents proxy-related errors
        http_client = httpx.Client(timeout=60.0)
        return OpenAI(api_key=api_key, http_client=http_client)
    except Exception as e:
        print(f"⚠️  OpenAI client initialization error: {e}")
        # Fallback: try with just api_key (less robust for proxy issues)
        try:
            return OpenAI(api_key=api_key)
        except Exception as e2:
            print(f"⚠️  Fallback initialization also failed: {e2}")
            return None


# ============================================================================
# Resume Evaluation Function
# ============================================================================
def evaluate_resume(resume_text: str, job_description: str):
    """
    Evaluate a resume against a job description using OpenAI GPT-4.
    
    This is the core Resume Evaluation Agent that:
    1. Constructs a detailed prompt with resume and job description
    2. Calls GPT-4 to analyze the match
    3. Returns structured JSON with evaluation scores
    
    Args:
        resume_text: Extracted text from the candidate's resume
        job_description: Job description text from the form
    
    Returns:
        dict: Structured evaluation with scores and summary, or None if error
        {
            "skills_match": float,
            "experience_years": int,
            "domain_relevance": float,
            "red_flags": list,
            "confidence": float,
            "summary": str
        }
    """
    # ========================================================================
    # Construct Evaluation Prompt
    # ========================================================================
    # The prompt instructs GPT-4 to analyze the resume and return structured JSON
    prompt = f"""
You are an HR AI assistant. Analyze the resume against the job description. 
Return ONLY JSON in this format:

{{
  "skills_match": float(0-1),
  "experience_years": int,
  "domain_relevance": float(0-1),
  "red_flags": list,
  "confidence": float(0-1),
  "summary": str
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""
    
    try:
        # ====================================================================
        # Initialize OpenAI Client
        # ====================================================================
        client = get_openai_client()
        if not client:
            print("❌ OpenAI API key not set or client initialization failed")
            return None
        
        # ====================================================================
        # Call OpenAI API
        # ====================================================================
        # Use GPT-4 with low temperature for consistent, deterministic results
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise JSON output generator. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1  # Low temperature for consistent results
        )
        
        # ====================================================================
        # Parse Response
        # ====================================================================
        # Extract JSON from response
        result = response.choices[0].message.content
        
        # Parse JSON string to dictionary
        data = json.loads(result)
        
        print(f"✅ Resume evaluation complete")
        print(f"   Skills Match: {data.get('skills_match', 'N/A')}")
        print(f"   Confidence: {data.get('confidence', 'N/A')}")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"   Raw response: {result[:200]}...")
        return None
    except Exception as e:
        print(f"❌ LLM evaluation error: {e}")
        return None
