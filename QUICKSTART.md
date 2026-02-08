# Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Activate virtual environment
# PowerShell (Windows):
.\myenv\Scripts\Activate.ps1

# Command Prompt (Windows):
myenv\Scripts\activate.bat

# Linux/Mac:
source myenv/bin/activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Install Tesseract OCR

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

## Step 3: Set Up Database

Create PostgreSQL database:
```sql
CREATE DATABASE agentic_hiring;
```

## Step 4: Configure Environment

Create `.env` file in project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_hiring
OPENAI_API_KEY=your_openai_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password_here
```

**For Gmail users:**
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password)

## Step 5: Initialize Database

```bash
python init_db.py
```

## Step 6: Run the Application

```bash
uvicorn app.main:app --reload
```

Visit: http://localhost:8000

## Troubleshooting

**Database connection error?**
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env

**OCR not working?**
- Verify Tesseract is installed: `tesseract --version`
- On Windows, may need to set path in code

**Email not sending?**
- Use App Password for Gmail (not regular password)
- Check SMTP settings in .env

## Need Help?

Run the setup checker:
```bash
python setup.py
```
