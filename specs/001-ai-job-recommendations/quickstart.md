# Quickstart: Developer Setup Guide

**Purpose**: Get backend & frontend running locally in <30 minutes  
**Date**: 2026-02-28  
**Prerequisites**: Python 3.10+, Node.js 18+, Docker (optional), Git

---

## Table of Contents

1. [Repository Setup](#repository-setup)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Database Setup](#database-setup)
5. [Running Services](#running-services)
6. [First API Test](#first-api-test)
7. [Common Issues](#common-issues)

---

## Repository Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/internship-recommendation-system.git
cd internship-recommendation-system
git checkout 001-ai-job-recommendations
```

### 2. Verify Branch
```bash
git branch -v
# Should show: * 001-ai-job-recommendations ...
```

### 3. Install Pre-commit Hooks (Optional)
```bash
pip install pre-commit
pre-commit install
```

---

## Backend Setup

### 1. Create Python Virtual Environment

**Windows (PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux (Bash)**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Python Dependencies

```bash
cd backend
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**requirements.txt includes**:
```
FastAPI==0.100.0
uvicorn[standard]==0.23.0
SQLAlchemy==2.0.0
alembic==1.12.0
psycopg2-binary==2.9.0
python-dotenv==1.0.0
pydantic==2.0.0
pydantic-settings==2.0.0
PyJWT==2.8.0
bcrypt==4.1.0
spacy==3.7.0
sentence-transformers==2.2.0
scikit-learn==1.3.0
numpy==1.24.0
pandas==2.1.0
requests==2.31.0
beautifulsoup4==4.12.0
PyMuPDF==1.23.0
python-docx==0.8.11
aiofiles==23.2.0
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
celery==5.3.0
APScheduler==3.10.0
```

### 3. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

Expected output: "✓ Download and installation successful"

### 4. Create .env File

**Create** `backend/.env`:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/internship_rec_db
SQLALCHEMY_ECHO=False

# JWT
SECRET_KEY=your-secret-key-change-in-production-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_TITLE="Internship & Job Recommendation System"
API_VERSION="1.0.0"
DEBUG=True

# File Upload
MAX_UPLOAD_SIZE_MB=10
ALLOWED_EXTENSIONS=pdf,docx,doc

# External APIs (optional)
OPENAI_API_KEY=sk-... # For GPT-4 chatbot (optional)

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=noreply@internships.local

# S3 (optional, for production)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=...
```

### 5. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed initial data (skills taxonomy)
python scripts/seed_skills.py
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
# or
yarn install
```

**package.json includes**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.19.0",
    "zustand": "^4.4.0",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0",
    "@headlessui/react": "^1.7.0",
    "react-icons": "^4.12.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "vitest": "^1.0.0",
    "@testing-library/react": "^14.1.0",
    "@testing-library/jest-dom": "^6.1.0",
    "cypress": "^13.6.0"
  }
}
```

### 3. Create Frontend .env File

**Create** `frontend/.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME="Internship Recommendations"
VITE_ENV=development
```

### 4. Verify Frontend Setup

```bash
npm run build
# Should complete with "✓ built in XXXms"
```

---

## Database Setup

### Option A: Docker (Recommended)

```bash
# From project root
docker-compose up postgres
# Wait for: "database system is ready to accept connections"

# In another terminal:
cd backend
alembic upgrade head
python scripts/seed_skills.py
```

### Option B: Local PostgreSQL Installation

**Windows**:
```powershell
# Install PostgreSQL from https://www.postgresql.org/download/windows/
# Or: choco install postgresql
# During installation, set password for 'postgres' user

# Open PowerShell, connect to psql:
psql -U postgres
```

**macOS**:
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu)**:
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

**Create Database & User**:
```sql
CREATE DATABASE internship_rec_db;
CREATE USER internship_user WITH PASSWORD 'your_secure_password';
ALTER ROLE internship_user SET client_encoding TO 'utf8';
ALTER ROLE internship_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE internship_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE internship_rec_db TO internship_user;
\c internship_rec_db
GRANT ALL PRIVILEGES ON SCHEMA public TO internship_user;
```

**Update .env**:
```env
DATABASE_URL=postgresql://internship_user:your_secure_password@localhost:5432/internship_rec_db
```

---

## Running Services

### 1. Start Backend Server

**Terminal 1 (from backend/ directory)**:
```bash
# Activate venv first (see Backend Setup step 1)
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\Activate.ps1  # Windows

# Start server
uvicorn main:app --reload --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

### 2. Start Frontend Dev Server

**Terminal 2 (from frontend/ directory)**:
```bash
npm run dev
```

**Expected output**:
```
VITE v5.0.0  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Press h to show help
```

### 3. (Optional) Start Background Job Scheduler

**Terminal 3 (from backend/ directory)**:
```bash
python -m APScheduler
# or
celery -A ml.job_scheduler worker --loglevel=info
```

---

## First API Test

### Test 1: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-02-28T10:00:00Z",
  "version": "1.0.0"
}
```

### Test 2: Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "John Doe",
    "location": "Bangalore, India",
    "phone": "+91-9876543210"
  }'
```

Expected response (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

### Test 3: Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

### Test 4: Upload Resume

```bash
TOKEN="<access_token_from_login>"
curl -X POST http://localhost:8000/api/v1/resumes/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_resume.pdf"
```

Expected response (201): Resume parsing results

### Test 5: Get Recommendations

```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/generate?location=Bangalore&limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

Expected response: Top 5 matching jobs

---

## Frontend Access

Open browser to: `http://localhost:5173`

**Test Flow**:
1. Click "Register" → fill form → submit
2. Login with credentials
3. Upload resume (PDF)
4. View recommendations
5. Bookmark/apply to jobs
6. View application tracker

---

## Running Tests

### Backend Unit Tests

```bash
cd backend
pytest tests/unit/ -v --cov=src
```

### Backend Integration Tests

```bash
# Ensure database is running
pytest tests/integration/ -v --cov=src
```

### Frontend Component Tests

```bash
cd frontend
npm run test:unit
```

### Frontend E2E Tests (Cypress)

```bash
# Start both backend and frontend first
npm run test:e2e
# Or interactive mode:
npx cypress open
```

---

## Useful Commands

### Database Operations

```bash
# Reset database (delete all data)
alembic downgrade base
alembic upgrade head
python scripts/seed_skills.py

# Check database status
psql -U internship_user -d internship_rec_db -c "\dt"

# Backup database
pg_dump -U internship_user internship_rec_db > backup.sql

# Restore database
psql -U internship_user internship_rec_db < backup.sql
```

### Backend Development

```bash
# Format code
black src tests

# Lint code
flake8 src tests

# Type checking
mypy src

# Check imports
isort src tests

# Generate API docs
# Automatically available at: http://localhost:8000/docs
```

### Frontend Development

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check (if TypeScript)
npm run type-check

# Build for production
npm run build
```

---

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'spacy'"

**Solution**:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

### Issue: "PostgreSQL connection refused"

**Solution**:
```bash
# Check if PostgreSQL is running
psql --version  # Should show version

# On macOS:
brew services start postgresql

# On Windows (PowerShell):
# Open Services.msc → find PostgreSQL → Start

# On Linux:
sudo service postgresql start
```

### Issue: "CORS error when frontend calls backend"

**Solution**: Backend needs CORS middleware enabled. In `backend/src/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Vite build fails with 'Cannot find module'"

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: "JWT token expired"

**Solution**: Login again to get new token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "...", "password": "..."}'
```

### Issue: ".env file not being read"

**Solution**: Ensure file is in correct location:
- Backend: `backend/.env` (read by FastAPI middleware)
- Frontend: `frontend/.env.local` (read by Vite)

Restart servers after creating .env files.

---

## Next Steps

1. ✅ Backend & frontend running locally
2. ✅ Database seeded with skills
3. ✅ API endpoints tested
4. ✅ Frontend accessible

**For Development**:
- See `ARCHITECTURE.md` for project structure details
- See `API.md` for complete endpoint documentation
- See `TESTING.md` for testing standards & coverage targets
- See `DEPLOYMENT.md` for production deployment steps

**For Deployment** (Later phases):
- Docker build: `docker build -t internship-rec-backend -f backend/Dockerfile .`
- Docker compose: `docker-compose up`
- Render deployment: Connect GitHub repo, auto-deploys on push
- AWS deployment: See `DEPLOYMENT.md`

---

**Quickstart Complete** ✅

You now have a fully functional development environment. Start with implementing unit tests for resume parser service next.

