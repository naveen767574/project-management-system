# Implementation Plan: AI-Based Internship & Job Recommendation System

**Branch**: `001-ai-job-recommendations` | **Date**: 2026-02-28 | **Spec**: [specs/001-ai-job-recommendations/spec.md](spec.md)
**Input**: Feature specification from `/specs/001-ai-job-recommendations/spec.md`

## Summary

Build a comprehensive, AI-powered job/internship recommendation platform that helps students discover matching opportunities through resume analysis, intelligent matching algorithms, and personalized AI guidance. The system prioritizes speed (<2s recommendations), accuracy (90% skill match), privacy (auto-delete resumes), and accessibility (works on low-end devices and poor connectivity). MVP focuses on resume parsing + recommendations + application tracking (P1 features); advanced features (job scraping, chatbot, career prediction) added in subsequent phases.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: FastAPI (backend), React + Vite (frontend), spaCy / Transformers (NLP), BeautifulSoup + Requests (scraping), Celery / APScheduler (background jobs)  
**Storage**: PostgreSQL (primary) with optional MongoDB for flexible job schema; S3 or local filesystem for resume storage  
**Testing**: pytest (backend), Vitest/RTL (frontend), integration tests for recommendation accuracy  
**Target Platform**: Web (responsive to 320px+), secondary desktop; mobile-first design; works on 2G/3G connections  
**Project Type**: Full-stack web application with async backend, React SPA frontend, NLP/ML data pipeline  
**Performance Goals**: 
- Recommendation generation <2 seconds (p95)
- Resume parsing <1 second
- API response ≤500ms 
- Database queries ≤200ms p95
- Handle ≥100 req/s concurrent load

**Constraints**:
- Lightweight deployment (FastAPI + React bundle <50MB)
- Optional external APIs (LinkedIn, Indeed scraping falls back to curated dataset)
- No permanent resume storage by default (7-day auto-delete)
- Low-literacy UI (minimal text, visual icons)
- Offline capability for cached recommendations

**Scale/Scope**: 
- Initial: 1000 students, 5000 job postings
- Growth: 10k students, 50k jobs by year 2
- LOC estimate: 8-12k lines (backend), 5-8k lines (frontend)
- UI screens: ~8 core screens (upload, recommendations, tracker, comparison, chatbot, resume builder, settings, admin)

---

## Constitution Check

### Gate 1: Core Principles Alignment (PASS ✅)

| Principle | Requirement | Plan Alignment | Status |
|-----------|------------|---|--------|
| **I. User-Centric Design & Accessibility** | UI distraction-free, mobile-first, works on low-end devices, dark mode, minimal text | React + Tailwind CSS responsive design, mobile-first approach, accessibility audit in QA phase, visual-heavy UI for low-literacy users | ✅ PASS |
| **II. AI-Driven Accuracy & Personalization** | ≥90% accuracy, interpretable models, explainable recommendations | spaCy NLP for skill extraction (90% benchmark), Sentence Transformers for semantic matching (explainable), rule-based fallback filters | ✅ PASS |
| **III. Performance & Speed** | FastAPI required, <2s recommendations, <1s parsing, lightweight deployment | FastAPI backend confirmed, async/await architecture, spaCy is lightweight, Vite for optimized bundle | ✅ PASS |
| **IV. Privacy & Trust** | 7-day auto-delete default, encrypt credentials, no black-box ML, audit logging | Resume expiration_date field (7-day default), JWT + bcrypt encryption, interpretable models (no deep neural nets), logging.info for security events | ✅ PASS |
| **V. Modern Engineering Practices** | Version control, code review, testing, CI/CD, documented decisions | Git flow enforced, pytest fixtures, GitHub Actions CI pipeline planned, ADR for major decisions (NLP model choice, storage type) | ✅ PASS |

**Gate 1 Result**: ✅ **PASS - All principles satisfied**

### Gate 2: Technical Feasibility (PASS ✅)

| Decision | Feasibility | Mitigation |
|----------|-------------|----------|
| spaCy for skill extraction | High - mature library, 90% accuracy achievable | Fallback regex patterns + manual skill taxonomy |
| Job scraping (LinkedI, Indeed) | Medium - may face blocks | Use APIs where available, rotate user-agents, fallback to curated dataset |
| Sentence Transformers for matching | High - proven semantic similarity | 500-skill taxonomy curated upfront |
| FastAPI + React stack | High - standard modern stack | Some developers may need FastAPI async ramp-up |
| 7-day auto-delete requirement | High - standard TTL pattern | Cron job (APScheduler) for batch deletion |

**Gate 2 Result**: ✅ **PASS - No blocking technical risks**

---

## Phase Completion Status

### ✅ Phase 0: Research (COMPLETE)
- **Output**: `specs/001-ai-job-recommendations/research.md` (200+ lines)
- **Artifacts**:
  - ✅ spaCy vs Transformers decision for skill extraction (spaCy + rule-based hybrid chosen)
  - ✅ Sentence Transformers for semantic similarity (proven, lightweight, <100ms inference)
  - ✅ Job scraping strategy (Phase 1: curated dataset + Indeed RSS + AngelList API + Internshala)
  - ✅ Chatbot approach (rule-based hardcoding + optional GPT-4 API for scope control)
  - ✅ Database choice: PostgreSQL primary + optional MongoDB for jobs (ACID, FK constraints, cost)
  - ✅ Authentication: JWT + bcrypt hash (standard pattern, offline-capable token validation)
  - ✅ Deployment options: Render (MVP) + AWS (production)
  - ✅ Resume auto-deletion: APScheduler cron job (7-day default TTL)
  - ✅ Performance benchmarks: Load testing approach validated
  - ✅ Skill taxonomy: 500-skill curated list (Programming, Frameworks, Data/ML, etc.)
- **All NEEDS CLARIFICATION items resolved** ✅

### ✅ Phase 1: Design (COMPLETE)
- **Output**: Data model, API contracts, service contracts, developer quickstart
- **Artifacts**:
  - ✅ `data-model.md` (300+ lines): 8 entities (users, resumes, skills, job_postings, recommendations, applications, chatbot_conversations, audit_logs) with relationships, validation rules, indexes, soft-delete support, 7-day TTL
  - ✅ `contracts/api-contract.md` (250+ lines): 6 endpoint groups (auth, resumes, recommendations, jobs, applications, chatbot) with request/response schemas, status codes, SLAs (<2s recommendations, <1s parsing)
  - ✅ `contracts/service-contract.md` (350+ lines): 4 service interfaces (ResumeParser, SkillTaxonomy, RecommendationEngine, Chatbot) with input/output contracts, algorithms, performance SLAs, error handling
  - ✅ `quickstart.md` (200+ lines): Step-by-step local setup (Python venv, npm, PostgreSQL, .env files, running services, first API tests)
  - ✅ Constitution re-validation: All gates still PASS post-design ✅
- **Ready for Phase 2: Implementation** ✅

### 🔄 Phase 2: Implementation (NEXT)
- **Scope**: Build backend services, frontend components, database layer
- **Approximate Task Breakdown**:
  - Backend Core (2 weeks): Database models, API routes, authentication middleware
  - NLP Services (1 week): Resume parser, skill taxonomy, similarity engine
  - Frontend Core (1.5 weeks): Layout, auth pages, resume upload UI
  - Integration & Testing (1 week): End-to-end flows, accuracy benchmarks, load tests
- **Entrance Gates**:
  - ✅ All research questions answered
  - ✅ All service contracts defined
  - ✅ Database schema frozen
  - ✅ API specification locked (can extend, not break existing contracts)

---

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-job-recommendations/
├── spec.md                          # Feature specification (COMPLETE ✅)
├── plan.md                          # Implementation plan (IN PROGRESS 🔄)
├── research.md                      # Phase 0: Technical research (COMPLETE ✅)
├── data-model.md                    # Phase 1: Data schema design (COMPLETE ✅)
├── quickstart.md                    # Phase 1: Developer quickstart (COMPLETE ✅)
├── contracts/
│   ├── api-contract.md              # REST API contract (COMPLETE ✅)
│   ├── service-contract.md          # NLP/ML service contracts (COMPLETE ✅)
│   └── [recommendation-contract.md] # Optional: detailed recommendation algorithm
└── checklists/
    └── requirements.md              # Requirements validation checklist (COMPLETE ✅)
```

### Source Code Structure (Web Application)

```text
backend/
├── src/
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Configuration, env vars
│   ├── models/
│   │   ├── user.py                  # User entity
│   │   ├── resume.py                # Resume entity
│   │   ├── job.py                   # JobPosting entity
│   │   ├── application.py           # Application tracker entity
│   │   ├── recommendation.py        # Recommendation entity
│   │   └── chatlog.py               # Chatbot conversation entity
│   ├── services/
│   │   ├── resume_parser.py         # NLP-based resume extraction
│   │   ├── recommendation_engine.py # Job matching algorithm
│   │   ├── job_scraper.py           # Job posting aggregation
│   │   ├── chatbot.py               # GPT/LLaMA integration
│   │   └── resume_builder.py        # Template-based resume generation
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py              # Login/signup
│   │   │   ├── resumes.py           # Resume upload/parse
│   │   │   ├── recommendations.py   # Job recommendations
│   │   │   ├── jobs.py              # Job search/details
│   │   │   ├── applications.py      # Application tracker
│   │   │   ├── chatbot.py           # Chat endpoint
│   │   │   └── admin.py             # Admin functions
│   │   ├── middleware.py            # Auth, CORS, logging middleware
│   │   └── schemas.py               # Pydantic request/response models
│   ├── database/
│   │   ├── connection.py            # DB initialization
│   │   ├── models.py                # SQLAlchemy ORM models
│   │   └── migrations/              # Alembic migrations
│   ├── ml/
│   │   ├── skill_extractor.py       # spaCy skill extraction
│   │   ├── similarity.py            # Semantic matching (Transformers)
│   │   ├── skill_taxonomy.json      # Curated 500-skill list
│   │   └── career_predictor.py      # ML model for 2/5/10 year prediction
│   ├── jobs/
│   │   ├── scrapers/
│   │   │   ├── internshala.py
│   │   │   ├── naukri.py
│   │   │   └── indeed.py
│   │   └── scheduler.py             # Celery/APScheduler for cron jobs
│   ├── utils/
│   │   ├── pdf_parser.py            # PDF → text conversion
│   │   ├── doc_parser.py            # DOCX → text conversion
│   │   ├── validators.py            # Email, resume, file validators
│   │   └── logging.py               # Structured logging
│   └── migrations/                  # Database schema migrations
├── tests/
│   ├── unit/
│   │   ├── test_resume_parser.py    # NLP extraction tests
│   │   ├── test_recommendation_engine.py
│   │   ├── test_validators.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_api_resume.py       # End-to-end resume upload
│   │   ├── test_api_recommendations.py  # Recommendation flow
│   │   └── test_db.py               # Database operations
│   ├── contract/
│   │   ├── test_resume_parser_schema.py  # Input/output validation
│   │   ├── test_api_contract.py     # OpenAPI compliance
│   │   └── test_recommendation_accuracy.py  # Accuracy benchmarks
│   └── fixtures/
│       ├── sample_resumes/          # Test resume files
│       ├── mock_jobs.json           # Test job data
│       └── conftest.py              # pytest configuration
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── README.md

frontend/
├── src/
│   ├── main.jsx                     # React app entry point
│   ├── App.jsx                      # Root component
│   ├── index.css                    # Global styles (Tailwind)
│   ├── components/
│   │   ├── ResumeUpload.jsx         # US1: Resume upload/parse
│   │   ├── RecommendationsList.jsx  # US2: Job recommendations display
│   │   ├── JobCard.jsx              # Individual job card
│   │   ├── Chatbot.jsx              # US3: Chat bubble + interface
│   │   ├── ApplicationTracker.jsx   # US4: Tracker view
│   │   ├── JobComparison.jsx        # US5: Side-by-side comparison
│   │   ├── ResumeBuilder.jsx        # US8: Resume generator
│   │   ├── CareerPredictor.jsx      # US7: Career path timeline
│   │   ├── Layout.jsx               # Header/menu/footer
│   │   ├── DarkModeToggle.jsx       # Dark mode switcher
│   │   └── LoadingSpinner.jsx       # Loading states
│   ├── pages/
│   │   ├── HomePage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── ApplicationsPage.jsx
│   │   ├── SettingsPage.jsx
│   │   └── AdminPage.jsx
│   ├── services/
│   │   ├── api.js                   # Axios API client
│   │   ├── auth.js                  # JWT token management
│   │   └── constants.js             # API URLs, limits
│   ├── store/
│   │   └── appStore.js              # Zustand state management
│   ├── utils/
│   │   ├── validators.js
│   │   ├── formatters.js
│   │   └── localStorage.js
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useRecommendations.js
│   │   └── useApplications.js
│   └── assets/
│       └── icons/                   # SVG icons (visual-heavy UI)
├── tests/
│   ├── components/
│   │   ├── ResumeUpload.test.jsx
│   │   ├── RecommendationsList.test.jsx
│   │   └── Chatbot.test.jsx
│   ├── services/
│   │   └── api.test.js
│   └── integration/
│       └── user-flow.test.jsx       # Full journey tests
├── e2e/
│   └── cypress.config.js            # Cypress e2e tests
├── vite.config.js
├── postcss.config.js
├── tailwind.config.js
├── package.json
├── .env.example
└── README.md

root/
├── docker-compose.yml               # Multi-container orchestration
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Tests on push
│       ├── build.yml                # Build & push Docker images
│       └── deploy.yml               # Auto-deploy to staging/prod
├── docs/
│   ├── ARCHITECTURE.md              # System design document
│   ├── API.md                       # API documentation
│   └── DEPLOYMENT.md                # Deployment guide
└── README.md
```

**Structure Decision**: Full-stack web application with separate backend (FastAPI) and frontend (React) directories. Chosen because:
1. Clear separation of concerns
2. Independent deployment of backend fixes (API) and frontend updates (UI changes)
3. Scalable: backend can serve multiple clients (web, mobile, third-party integrations)
4. Testing: each layer independently testable (unit tests for services, contract tests for API, E2E tests for flows)

---

## Complexity Tracking

> No Constitution violations requiring justification at this time. All design choices align with core principles.

**Optional Complexity Decisions for Future Re-evaluation**:

| Decision | Why Might Be Needed | Current Plan | Re-evaluate If |
|----------|-------------------|--------------|---|
| Separate ML service (microservice) | Scale NLP pipeline independently | Colocate in FastAPI for MVP | Recommendation latency >2s or skill extraction latency >1s |
| Cache layer (Redis) | Reduce DB queries for popular jobs | In-memory caching + HTTP caching headers (MVP) | QPS >200 or recommendation generation exceeds 2s |
| Message queue (RabbitMQ) beyond Celery | Handle high-volume job scraping | APScheduler + Celery for background tasks (MVP) | Scraping jobs fail >5% or exceed 2-hour completion window |
| Multi-region deployment | Scale to international students | Single region (AWS EC2/RDS) for MVP | User base expands beyond 10k students |
