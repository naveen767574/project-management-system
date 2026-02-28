# API Contract: Backend Service

**Purpose**: OpenAPI specification for FastAPI backend endpoints  
**Version**: 1.0.0  
**Date**: 2026-02-28

---

## Overview

RESTful API with JSON request/response. All requests require valid JWT token in `Authorization: Bearer <token>` header (except `/auth/register` and `/auth/login`).

**Base URL**: `http://localhost:8000/api/v1`  
**Response Format**: JSON  
**Authentication**: JWT tokens (7-day expiry)

---

## Auth Endpoints

### POST /auth/register
Register new user account.

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "location": "Bangalore, India",
  "phone": "+91-9876543210"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "full_name": "John Doe",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

**Status Codes**:
- `201`: Registration successful
- `400`: Invalid input (weak password, invalid email, etc.)
- `409`: Email already registered

---

### POST /auth/login
Authenticate user and get JWT token.

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes**:
- `200`: Login successful
- `401`: Invalid credentials
- `404`: User not found

---

### POST /auth/refresh
Refresh JWT token (optionally before expiry).

**Request** (empty body, use current token):
```
Authorization: Bearer <current_token>
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800
}
```

---

## Resume Endpoints

### POST /resumes/upload
Upload and parse resume.

**Request** (multipart/form-data):
```
- file: <PDF or DOCX binary>
- auto_delete_enabled: true/false (optional, default: true)
- retention_days: 7 (optional, default: 7)
```

**Response** (201 Created):
```json
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_name": "john_resume.pdf",
  "quality_score": 85,
  "extraction_confidence": 0.92,
  "parsed_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+91-9876543210",
    "location": "Bangalore",
    "education": [
      {
        "degree": "B.Tech",
        "field": "Computer Science",
        "institution": "IIT Bombay",
        "graduation_year": 2023,
        "cgpa": 7.5
      }
    ],
    "experience": [
      {
        "company": "Google",
        "position": "SDE Intern",
        "start_date": "2022-06",
        "end_date": "2022-09",
        "description": "Worked on..."
      }
    ],
    "skills": [
      {
        "name": "Python",
        "proficiency": "expert",
        "years_of_experience": 4
      },
      {
        "name": "React",
        "proficiency": "intermediate",
        "years_of_experience": 2
      }
    ]
  },
  "created_at": "2026-02-28T10:30:00Z",
  "expiration_date": "2026-03-07T00:00:00Z"
}
```

**Status Codes**:
- `201`: Resume uploaded and parsed successfully
- `400`: Invalid file format, file too large (>10MB), or parsing failed
- `401`: Unauthorized (missing/invalid token)

---

### GET /resumes/{resume_id}
Get parsed resume details.

**Response** (200 OK):
```json
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440001",
  "quality_score": 85,
  "extraction_confidence": 0.92,
  "parsed_data": { ... },
  "created_at": "2026-02-28T10:30:00Z",
  "expiration_date": "2026-03-07T00:00:00Z"
}
```

---

### GET /resumes/current
Get current active resume for authenticated user.

**Response** (200 OK): Same as GET /resumes/{resume_id}

**Status Codes**:
- `200`: Resume found
- `404`: No active resume (user hasn't uploaded any)

---

## Recommendation Endpoints

### POST /recommendations/generate
Generate job recommendations for user's resume.

**Request** (POST with query params):
```
POST /recommendations/generate?location=Bangalore&experience_level=fresher&limit=7
Authorization: Bearer <token>
Content-Type: application/json

{
  "filter_locations": ["Bangalore", "Pune"],           // optional
  "filter_experience_levels": ["fresher"],            // optional
  "filter_job_type": ["internship", "full-time"],     // optional
  "min_salary_lpa": 3,                                // optional
  "limit": 7                                          // default: 7, max: 20
}
```

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "resume_id": "550e8400-e29b-41d4-a716-446655440001",
  "recommendation_count": 7,
  "generated_at": "2026-02-28T10:35:00Z",
  "recommendations": [
    {
      "rank": 1,
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Backend Engineer (Python)",
      "company": "Flipkart",
      "location": "Bangalore",
      "match_percentage": 92,
      "explanation": "Matches 5 of your 5 key skills: Python, PostgreSQL, React, Docker, AWS",
      "matched_skills": ["Python", "PostgreSQL", "React", "Docker", "AWS"],
      "missing_skills": [],
      "salary_min_lpa": 6,
      "salary_max_lpa": 10,
      "job_type": "full-time",
      "experience_level": "associate",
      "posting_date": "2026-02-15T00:00:00Z",
      "source_url": "https://careers.flipkart.com/..."
    },
    {
      "rank": 2,
      "job_id": "550e8400-e29b-41d4-a716-446655440003",
      "title": "Frontend Engineer (React)",
      "company": "Amazon",
      "location": "Bangalore",
      "match_percentage": 78,
      "explanation": "Matches 4 of 5 required skills. Missing: Kubernetes",
      "matched_skills": ["JavaScript", "React", "TypeScript", "CSS"],
      "missing_skills": ["Kubernetes"],
      "salary_min_lpa": 8,
      "salary_max_lpa": 12,
      ...
    }
  ]
}
```

**Status Codes**:
- `200`: Recommendations generated successfully
- `400`: Invalid filters or limit out of range
- `404`: User has no active resume
- `408`: Recommendation engine timeout (>2s)

**Performance SLA**: Max 2 seconds response time

---

### GET /recommendations/recent
Get previously generated recommendations for user.

**Query Params**:
- `limit`: Number of results (default: 10, max: 50)
- `offset`: Pagination offset (default: 0)

**Response** (200 OK): Array of recommendations with pagination metadata

```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "recommendations": [ ... ]
}
```

---

## Job Posting Endpoints

### GET /jobs/search
Search job postings with filters.

**Query Params**:
```
GET /jobs/search?
  location=Bangalore&
  company=Google&
  job_type=internship&
  experience_level=fresher&
  min_salary=2&
  max_salary=5&
  search_keywords=Python+Backend&
  limit=20&
  offset=0
```

**Response** (200 OK):
```json
{
  "total": 342,
  "limit": 20,
  "offset": 0,
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Backend Engineer (Python)",
      "company": "Flipkart",
      "location": "Bangalore",
      "job_type": "full-time",
      "experience_level": "associate",
      "salary_min_lpa": 6,
      "salary_max_lpa": 10,
      "required_skills": [
        { "name": "Python", "required": true, "years_min": 2 },
        { "name": "PostgreSQL", "required": true, "years_min": 1 },
        { "name": "React", "required": false, "years_min": 1 }
      ],
      "source": "Indeed",
      "posting_date": "2026-02-15T00:00:00Z",
      "expiration_date": "2026-03-20T00:00:00Z",
      "url": "https://indeed.com/..."
    }
  ]
}
```

**Status Codes**: `200` OK, `400` Invalid filters

---

### GET /jobs/{job_id}
Get detailed job posting.

**Response** (200 OK): Single job object with full details

---

## Application Tracking Endpoints

### POST /applications
Create new application record.

**Request**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "applied",
  "notes": "Applied via online portal"
}
```

**Response** (201 Created):
```json
{
  "application_id": "550e8400-e29b-41d4-a716-446655440010",
  "job_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "applied",
  "applied_at": "2026-02-28T10:40:00Z",
  "notes": "Applied via online portal"
}
```

---

### GET /applications
List all applications for user.

**Query Params**:
- `status`: Filter by status (applied, interview_scheduled, etc.)
- `limit`: Default 20, max 100
- `offset`: Pagination

**Response** (200 OK):
```json
{
  "total": 15,
  "limit": 20,
  "offset": 0,
  "applications": [
    {
      "application_id": "550e8400-e29b-41d4-a716-446655440010",
      "job_id": "550e8400-e29b-41d4-a716-446655440002",
      "job_title": "Backend Engineer",
      "company": "Flipkart",
      "status": "applied",
      "applied_at": "2026-02-27T15:00:00Z",
      "notes": "..."
    }
  ]
}
```

---

### PUT /applications/{application_id}
Update application status.

**Request**:
```json
{
  "status": "interview_scheduled",
  "interview_date": "2026-03-05T14:00:00Z",
  "notes": "Final round interview"
}
```

**Response** (200 OK): Updated application object

---

## Chatbot Endpoints

### POST /chatbot/message
Send message to chatbot.

**Request**:
```json
{
  "message": "What skills should I learn for data science?",
  "language": "en"
}
```

**Response** (200 OK):
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440011",
  "response": "To start a data science career, you should focus on: 1. Python (essential), 2. Statistics & Probability, 3. SQL for database querying, 4. Machine Learning libraries (scikit-learn, TensorFlow), 5. Data visualization (Matplotlib, Tableau).",
  "response_type": "rule_based",
  "confidence": 0.95,
  "message_id": "550e8400-e29b-41d4-a716-446655440012"
}
```

**Status Codes**: `200` OK, `400` Invalid message format

---

### GET /chatbot/history
Get conversation history.

**Query Params**:
- `limit`: Default 20, max 100
- `offset`: Pagination

**Response** (200 OK):
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440011",
  "messages": [
    {
      "role": "user",
      "content": "What skills for data science?",
      "timestamp": "2026-02-28T09:00:00Z"
    },
    {
      "role": "assistant",
      "content": "To start data science...",
      "timestamp": "2026-02-28T09:00:05Z"
    }
  ]
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format. Only PDF and DOCX supported.",
    "details": [
      {
        "field": "file",
        "message": "File type .xls not supported"
      }
    ]
  }
}
```

**Common Error Codes**:
- `VALIDATION_ERROR`: 400 Bad Request
- `AUTHENTICATION_ERROR`: 401 Unauthorized
- `NOT_FOUND`: 404 Not Found
- `RATE_LIMIT`: 429 Too Many Requests
- `INTERNAL_ERROR`: 500 Internal Server Error

---

## Rate Limiting

- **Resume Upload**: 5 per day per user
- **Recommendation Generation**: 30 per day per user
- **Chatbot Messages**: 100 per day per user
- **General API**: 1000 requests per hour per user

Response includes:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 956
X-RateLimit-Reset: 1677609600
```

---

## File Upload Constraints

- **Max Size**: 10 MB per file
- **Allowed Formats**: PDF, DOCX, DOC
- **Timeout**: 30 seconds

---

This contract is implemented via FastAPI route handlers in `backend/src/api/routes/`.

