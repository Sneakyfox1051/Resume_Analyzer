# Render Deployment Guide

## Prerequisites
1. GitHub account with your code pushed to a repository
2. Render account (sign up at https://render.com)

## Deployment Steps

### 1. Create PostgreSQL Database on Render
1. Go to Render Dashboard → New → PostgreSQL
2. Name: `resume_analyzer_db` (or any name you prefer)
3. Plan: Free (or paid for production)
4. Click "Create Database"
5. Note the **Internal Database URL** (you'll need this if not using render.yaml)

### 2. Create Web Service

#### Option A: Using render.yaml (Recommended)
1. Go to Render Dashboard → New → Blueprint
2. Connect your GitHub repository
3. Select the repository: `Sneakyfox1051/Resume_Analyzer`
4. Render will automatically detect `render.yaml` and configure everything
5. Click "Apply" to deploy

#### Option B: Manual Setup
1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Select: `Sneakyfox1051/Resume_Analyzer`
4. Configure:
   - **Name**: `resume-analyzer`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python init_db.py`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or paid)

### 3. Set Environment Variables

In your Render Web Service dashboard, go to "Environment" and add:

- `DATABASE_URL`: 
  - If using render.yaml: Auto-filled from linked database
  - If manual: Use Internal Database URL from PostgreSQL service
- `OPENAI_API_KEY`: `sk-proj-...` (your OpenAI API key)
- `SMTP_SERVER`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `SMTP_USER`: `adabbawa10@gmail.com`
- `SMTP_PASS`: `ccgfdsohymdvgixw`

**Important**: Never commit these values to GitHub. Set them only in Render dashboard.

### 4. Link Database (if manual setup)

1. In your Web Service dashboard
2. Go to "Environment" tab
3. Find "Add Environment Variable"
4. Add `DATABASE_URL` and select your PostgreSQL database from the dropdown
5. Render will auto-fill the connection string

### 5. Deploy

Click "Create Web Service" (or "Apply" for Blueprint) and Render will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Run `init_db.py` to create database tables
4. Start your application with uvicorn

### 6. Access Your App

Once deployed, Render provides a URL like:
`https://resume-analyzer.onrender.com`

- **Web Interface**: `https://resume-analyzer.onrender.com`
- **API Docs**: `https://resume-analyzer.onrender.com/docs`

## Important Notes

### Database
- **Render uses PostgreSQL**, not SQLite
- The `DATABASE_URL` is automatically provided by Render
- Database tables are created during build via `init_db.py`

### Port Configuration
- **Always use `$PORT`** environment variable (Render sets this automatically)
- **Host must be `0.0.0.0`** to accept connections from Render's load balancer
- Never hardcode port numbers

### Environment Variables
- **Never commit `.env` file** to GitHub
- Set all sensitive values in Render dashboard
- `DATABASE_URL` is auto-linked if using render.yaml

### Free Tier Limitations
- **Services spin down** after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds (cold start)
- Consider upgrading to paid plan for production use

### Build Process
1. Render installs dependencies: `pip install -r requirements.txt`
2. Initializes database: `python init_db.py`
3. Starts server: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Troubleshooting

#### Build Fails
- Check `requirements.txt` for correct package versions
- Verify Python version in `runtime.txt` matches Render's supported versions
- Check build logs in Render dashboard

#### Database Connection Errors
- Verify `DATABASE_URL` is set correctly
- Ensure database is linked to web service
- Check database is running (not paused)

#### Application Crashes
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `init_db.py` ran successfully

#### Slow First Request
- Normal on free tier (cold start)
- Consider upgrading to paid plan for faster response times

## Updating Your Deployment

After pushing changes to GitHub:
1. Render automatically detects changes
2. Triggers a new deployment
3. Rebuilds and redeploys your application

You can also manually trigger deployments from Render dashboard.

## Monitoring

- View logs in real-time from Render dashboard
- Set up alerts for deployment failures
- Monitor database usage and performance
