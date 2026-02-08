"""
================================================================================
UTILITY FUNCTIONS - Resume Text Extraction
================================================================================

This module provides functions for extracting text from PDF resumes.

Features:
1. Normal PDF text extraction (for text-based PDFs)
2. OCR (Optical Character Recognition) for scanned/image-based PDFs
3. Smart extraction that automatically chooses the best method
4. Text cleaning and normalization

The smart extraction strategy:
- First tries normal PDF text extraction (fast, works for most PDFs)
- Falls back to OCR if extracted text is too short (< 300 chars)
- This handles both text-based and scanned PDFs automatically
"""

import pdfplumber
import re
import pytesseract
from pdf2image import convert_from_bytes


# ============================================================================
# FUNCTION 1: Normal PDF Text Extraction
# ============================================================================
def extract_text_from_pdf(file):
    """
    Extract text from a text-based PDF file using pdfplumber.
    
    This method works for PDFs that contain actual text (not scanned images).
    It's fast and accurate for most modern PDFs.
    
    Args:
        file: File-like object or file path to the PDF
    
    Returns:
        str: Extracted text from all pages, or empty string if extraction fails
    """
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            # Extract text from each page
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    
    return text.strip()


# ============================================================================
# FUNCTION 2: OCR Text Extraction (for Scanned PDFs)
# ============================================================================
def extract_text_with_ocr(file_bytes):
    """
    Extract text from scanned/image-based PDFs using OCR (Optical Character Recognition).
    
    This method converts PDF pages to images and then uses Tesseract OCR
    to extract text. Slower than normal extraction but works for scanned PDFs.
    
    Requirements:
    - Tesseract OCR must be installed on the system
    - pdf2image library for PDF to image conversion
    
    Args:
        file_bytes: Raw bytes of the PDF file
    
    Returns:
        str: Extracted text from all pages using OCR
    """
    text = ""
    try:
        # Convert PDF pages to images
        images = convert_from_bytes(file_bytes)
        
        # Extract text from each image using OCR
        for img in images:
            ocr_text = pytesseract.image_to_string(img)
            if ocr_text:
                text += ocr_text + "\n"
    except Exception as e:
        print(f"OCR extraction error: {e}")
    
    return text.strip()


# ============================================================================
# FUNCTION 3: Smart Extraction (with Automatic Fallback)
# ============================================================================
def extract_resume_text(file):
    """
    Smart extraction that tries normal PDF extraction first, then falls back to OCR.
    
    Strategy:
    1. Try normal PDF text extraction (fast)
    2. If extracted text is too short (< 300 chars), likely a scanned PDF
    3. Fall back to OCR extraction
    4. Clean and normalize the final text
    
    Args:
        file: File-like object to the PDF
    
    Returns:
        str: Cleaned and normalized extracted text
    """
    # Read file bytes for potential OCR use
    file_bytes = file.read()
    file.seek(0)  # Reset file pointer for pdfplumber
    
    # Try normal extraction first
    text = extract_text_from_pdf(file)
    
    # Heuristic: Scanned PDFs usually produce very little text
    # If text is too short, likely a scanned PDF - use OCR
    if len(text) < 300:
        print("Low text detected, running OCR...")
        text = extract_text_with_ocr(file_bytes)
    
    # Clean and return normalized text
    return clean_resume_text(text)


# ============================================================================
# FUNCTION 4: Text Cleaning and Normalization
# ============================================================================
def clean_resume_text(text: str) -> str:
    """
    Clean and normalize extracted resume text.
    
    Removes:
    - Excessive newlines (multiple consecutive newlines)
    - Excessive whitespace (multiple spaces)
    
    Args:
        text: Raw extracted text
    
    Returns:
        str: Cleaned and normalized text
    """
    # Replace multiple newlines with single newline
    text = re.sub(r'\n+', '\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()
