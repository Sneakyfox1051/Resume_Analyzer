# Resume Analyzer - Agentic AI HR Pipeline

An intelligent HR automation system that uses AI to evaluate resumes, make initial hiring decisions, and automate email communications. The system includes a human-in-the-loop review process for cases that need additional scrutiny.

## Features

- **Resume Processing**: PDF text extraction with OCR fallback for scanned documents
- **AI-Powered Evaluation**: Uses OpenAI GPT-4 to analyze resumes against job descriptions
- **Decision Engine**: Automated decision-making with confidence thresholds
- **Human Review Interface**: Web-based interface for manual review of borderline cases
- **Email Automation**: Automated email notifications for candidates based on decisions
- **Database Logging**: Complete audit trail of all decisions and communications

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database (optional - defaults to SQLite for local development)
- OpenAI API key
- Tesseract OCR (for PDF OCR functionality)
- SMTP email account (Gmail, Outlook, etc.)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sneakyfox1051/Resume_Analyzer.git
cd Resume_Analyzer
```

### 2. Set up virtual environment

The project already has a virtual environment (`myenv`). Activate it:

**Windows PowerShell:**
```powershell
.\myenv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
myenv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source myenv/bin/activate
```

If you need to create a new virtual environment:
```bash
python -m venv myenv
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Or use: `choco install tesseract`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### 5. Set up Database

**For Local Development (SQLite - Default):**
- No setup needed! The app defaults to SQLite for easy local development
- Database file: `agentic_hiring.db` (created automatically)

**For Production (PostgreSQL):**
- Create a PostgreSQL database
- Set `DATABASE_URL` in `.env` file
- Example: `DATABASE_URL=postgresql://user:password@localhost:5432/agentic_hiring`

### 6. Configure environment variables

Copy the example environment file and fill in your values:

```bash
copy .env.example .env
```

Edit `.env` and update:
- `DATABASE_URL`: Your PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`: Your email server credentials

**For Gmail:**
- Use an App Password (not your regular password)
- Enable 2-factor authentication
- Generate App Password: https://myaccount.google.com/apppasswords

### 7. Initialize the database

Run the database initialization script:

```bash
python init_db.py
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Web Interface**: http://localhost:8000

## Usage

### 1. Submit a Resume

- Navigate to http://localhost:8000
- Enter a job description
- Upload a PDF resume
- The system will automatically:
  - Extract text from the resume
  - Evaluate it against the job description
  - Make an initial decision (SHORTLIST, REJECT, or NEEDS_HUMAN_REVIEW)
  - Send automated emails for final decisions

### 2. Human Review

For cases flagged as `NEEDS_HUMAN_REVIEW`:
- Navigate to `/review/{candidate_id}`
- Review the AI evaluation summary
- Make a final decision (SHORTLIST or REJECT)
- Add optional comments
- Submit to trigger automated email

## Project Structure

```
Resume_Analyzer/
├── app/
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database connection and session
│   ├── resume_agent.py      # OpenAI resume evaluation
│   ├── decision_engine.py   # Decision-making logic
│   ├── email_agent.py       # Email automation
│   ├── utils.py             # PDF extraction and OCR utilities
│   └── templates/
│       ├── index.html       # Resume submission form
│       ├── review.html      # Human review interface
│       ├── candidates.html # Candidates dashboard
│       └── candidate_detail.html # Candidate details page
├── requirements.txt         # Python dependencies
├── init_db.py              # Database initialization script
└── README.md               # This file
```

## API Endpoints

- `GET /` - Resume submission form
- `POST /submit_resume/` - Submit resume for evaluation
- `GET /review/{candidate_id}` - Human review page
- `POST /review/{candidate_id}` - Submit human review decision
- `GET /docs` - Interactive API documentation

## Decision Logic

The system uses the following rules:

- **SHORTLIST**: Confidence ≥ 0.8 AND skills_match ≥ 0.75
- **REJECT**: Confidence ≤ 0.4
- **NEEDS_HUMAN_REVIEW**: All other cases

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists: `CREATE DATABASE agentic_hiring;`

### OCR Not Working
- Verify Tesseract is installed: `tesseract --version`
- Check Tesseract is in PATH
- For Windows, may need to set path in code: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### Email Not Sending
- Verify SMTP credentials in `.env`
- For Gmail, use App Password (not regular password)
- Check firewall/network settings
- Review email logs in database

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits
- Review rate limits

## Development

### Running in Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

For production, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
