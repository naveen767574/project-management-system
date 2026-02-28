# Data Model: AI-Based Internship & Job Recommendation System

**Phase**: 1 (Design)  
**Date**: 2026-02-28  
**Purpose**: Define database schema, entities, relationships, and validation rules

---

## Overview

The system uses **PostgreSQL** as primary data store with ACID guarantees and referential integrity. All timestamps in UTC. All IDs are UUID v4 or auto-incrementing integers.

---

## Entity: `users`

Represents system users (students/job seekers).

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,  -- bcrypt(password)
  full_name VARCHAR(255),
  phone VARCHAR(20),
  location VARCHAR(255),                -- city, country
  experience_level ENUM('fresher', 'associate', 'mid-level', 'senior'),
  preferred_languages TEXT[] DEFAULT ARRAY['en'],
  dark_mode BOOLEAN DEFAULT false,
  resume_public BOOLEAN DEFAULT false,  -- allow sharing with employers
  auto_delete_resume BOOLEAN DEFAULT true,
  resume_retention_days INTEGER DEFAULT 7,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login_at TIMESTAMP,
  deleted_at TIMESTAMP,                 -- soft delete
  
  CONSTRAINT valid_email CHECK (email ~ '^[^@]+@[^@]+\.[^@]+$'),
  CONSTRAINT valid_phone CHECK (phone ~ '^\+?[0-9\-\s()]{7,}$' OR phone IS NULL)
);
```

**Attributes**:
- `id`: Unique user identifier
- `email`: Login credential, must be unique
- `password_hash`: bcrypt hash (never store plaintext)
- `location`: Used for job filtering
- `experience_level`: Fresher/Associate/Mid-level/Senior (auto-inferred from resume)
- `preferred_languages`: Array of language codes (en, hi, ta, te) for UI/chatbot
- `dark_mode`: UI preference
- `auto_delete_resume`: Privacy flag (default true for auto-deletion)
- `created_at`: Account creation timestamp
- `deleted_at`: Soft-delete support for account closure

**Indexes**:
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_location ON users(location);
CREATE INDEX idx_users_deleted ON users(deleted_at);
```

---

## Entity: `resumes`

Represents parsed resume data with extracted skills.

```sql
CREATE TABLE resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Original file metadata
  file_name VARCHAR(255),
  file_type ENUM('pdf', 'docx', 'doc', 'txt'),
  file_size_bytes INTEGER,
  file_hash VARCHAR(64),                -- SHA256 for deduplication
  
  -- Parsed data (JSONB for flexibility)
  parsed_data JSONB NOT NULL,           -- {name, email, phone, education[], experience[], skills[], certifications[], projects[]}
  
  -- Metadata
  quality_score INTEGER CHECK (quality_score BETWEEN 0 AND 100),  -- 0-100, based on completeness
  extraction_confidence DECIMAL(3,2),   -- 0.0-1.0, average confidence in NER
  
  -- Privacy & Retention
  expiration_date TIMESTAMP,            -- auto-delete date (7 days by default)
  is_deleted BOOLEAN DEFAULT false,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  parsed_at TIMESTAMP,
  deleted_at TIMESTAMP,
  
  CONSTRAINT one_active_resume_per_user UNIQUE(user_id, is_deleted) 
                                         WHERE (is_deleted = false)
);
```

**Parsed Data Structure** (JSONB):
```json
{
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
      "duration_months": 3,
      "start_date": "2022-06",
      "end_date": "2022-09",
      "description": "Worked on..."
    }
  ],
  "skills": [
    {
      "name": "Python",
      "proficiency": "expert",
      "mentioned_count": 5,
      "years_of_experience": 4
    }
  ],
  "certifications": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "AWS",
      "date": "2023-01"
    }
  ],
  "projects": [
    {
      "name": "E-commerce Platform",
      "description": "...",
      "url": "github.com/..."
    }
  ]
}
```

**Attributes**:
- `parsed_data`: JSONB for flexibility (resume formats vary greatly)
- `quality_score`: 0-100 based on completeness (all sections filled → higher score)
- `extraction_confidence`: Average confidence from NER model
- `expiration_date`: Auto-delete timestamp (privacy-first)
- `is_deleted`: Soft-delete flag

**Indexes**:
```sql
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_expiration ON resumes(expiration_date) WHERE is_deleted = false;
CREATE INDEX idx_resumes_quality ON resumes(quality_score);
```

---

## Entity: `skills`

Master list of skills extracted from resumes and job postings.

```sql
CREATE TABLE skills (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,    -- "Python", "React", "AWS"
  category VARCHAR(100),                 -- "Programming Language", "Framework", "Cloud"
  proficiency_levels TEXT[] DEFAULT ARRAY['beginner', 'intermediate', 'expert'],
  is_active BOOLEAN DEFAULT true,        -- for soft-deleting obsolete skills
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT skill_name_length CHECK (LENGTH(name) >= 2)
);
```

**Sample Data**:
```sql
INSERT INTO skills (name, category) VALUES
  ('Python', 'Programming Language'),
  ('JavaScript', 'Programming Language'),
  ('React', 'Web Framework'),
  ('PostgreSQL', 'Database'),
  ('AWS', 'Cloud Platform'),
  ('Docker', 'DevOps'),
  ('Machine Learning', 'Specialization');
```

**Indexes**:
```sql
CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_category ON skills(category);
```

---

## Entity: `job_postings`

Job opportunities aggregated from multiple sources.

```sql
CREATE TABLE job_postings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Job Content
  title VARCHAR(255) NOT NULL,
  company_name VARCHAR(255) NOT NULL,
  description TEXT,
  
  -- Location & Remote
  location VARCHAR(255),                -- city, state, country
  is_remote BOOLEAN DEFAULT false,
  
  -- Compensation
  salary_min_lpa DECIMAL(6,2),          -- in Indian Rupees/Lakhs Per Annum
  salary_max_lpa DECIMAL(6,2),
  currency VARCHAR(3) DEFAULT 'INR',
  
  -- Job Details
  job_type ENUM('internship', 'full-time', 'contract', 'part-time'),
  experience_level ENUM('fresher', 'associate', 'mid-level', 'senior'),
  
  -- Required Skills (JSONB array)
  required_skills JSONB NOT NULL,       -- [{name: "Python", required: true, years_min: 2}, ...]
  
  -- Source & Tracking
  source_url VARCHAR(500),
  source_name VARCHAR(100),              -- "Indeed", "LinkedIn", "Internshala", "Naukri"
  source_job_id VARCHAR(255),
  
  -- Metadata
  posting_date TIMESTAMP,
  expiration_date TIMESTAMP,
  scraping_date TIMESTAMP,
  last_seen_date TIMESTAMP,
  is_active BOOLEAN DEFAULT true,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT salary_range CHECK (salary_max_lpa >= salary_min_lpa OR salary_min_lpa IS NULL)
);
```

**Required Skills Structure** (JSONB):
```json
[
  {
    "name": "Python",
    "required": true,
    "years_min": 2,
    "proficiency_min": "intermediate"
  },
  {
    "name": "React",
    "required": false,
    "years_min": 1,
    "proficiency_min": "beginner"
  }
]
```

**Indexes**:
```sql
CREATE INDEX idx_jobs_company ON job_postings(company_name);
CREATE INDEX idx_jobs_location ON job_postings(location);
CREATE INDEX idx_jobs_source ON job_postings(source_name);
CREATE INDEX idx_jobs_posting_date ON job_postings(posting_date);
CREATE INDEX idx_jobs_expiration ON job_postings(expiration_date) WHERE is_active = true;
CREATE INDEX idx_jobs_required_skills ON job_postings USING gin(required_skills);
```

---

## Entity: `recommendations`

System-generated job recommendations for users.

```sql
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
  
  -- Scoring
  match_percentage INTEGER NOT NULL CHECK (match_percentage BETWEEN 0 AND 100),
  semantic_score DECIMAL(3,2),          -- 0.0-1.0 from Sentence Transformers
  keyword_score DECIMAL(3,2),           -- 0.0-1.0 from TF-IDF
  
  -- Explanation
  explanation_text TEXT,                -- "Matches 4 of 5 required skills: Python, React, PostgreSQL..."
  matched_skills TEXT[],                -- ["Python", "React", "PostgreSQL"]
  missing_skills TEXT[],                -- ["Kubernetes"]
  
  -- User Interaction
  was_clicked BOOLEAN DEFAULT false,
  was_bookmarked BOOLEAN DEFAULT false,
  was_applied BOOLEAN DEFAULT false,
  click_timestamp TIMESTAMP,
  
  -- Ranking
  rank_position INTEGER,                -- 1-7, position in recommendation list
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_recommendation UNIQUE(user_id, job_id)
);
```

**Attributes**:
- `match_percentage`: 0-100%, computed from semantic + keyword scores
- `semantic_score`: From Sentence Transformers embedding similarity
- `keyword_score`: From resume skill overlap with job requirements
- `explanation_text`: Human-readable explanation (shown to user)
- `was_clicked`: Tracks user engagement

**Indexes**:
```sql
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_job_id ON recommendations(job_id);
CREATE INDEX idx_recommendations_match_pct ON recommendations(match_percentage DESC);
CREATE INDEX idx_recommendations_created ON recommendations(user_id, created_at DESC);
```

---

## Entity: `applications`

Track user job applications.

```sql
CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES job_postings(id) ON DELETE SET NULL,
  
  -- Status Tracking
  status ENUM('applied', 'interview_scheduled', 'rejected', 'rejected_by_user', 'offer_received', 'offer_accepted'),
  status_updated_at TIMESTAMP,
  
  -- Details
  applied_at TIMESTAMP DEFAULT NOW(),
  interview_date TIMESTAMP,
  notes TEXT,                           -- user's notes about the application
  
  -- Reminders
  next_reminder_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT unique_application UNIQUE(user_id, job_id)
);
```

**Status Workflow**:
```
applied → interview_scheduled → offer_received → offer_accepted
      ↘  rejected
      ↘  rejected_by_user
```

**Indexes**:
```sql
CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_reminder ON applications(next_reminder_at) WHERE next_reminder_at IS NOT NULL;
CREATE INDEX idx_applications_applied_date ON applications(user_id, applied_at DESC);
```

---

## Entity: `chatbot_conversations`

Store chatbot interaction history for learning & debugging.

```sql
CREATE TABLE chatbot_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  session_id VARCHAR(255),              -- session identifier
  message_count INTEGER DEFAULT 0,
  
  created_at TIMESTAMP DEFAULT NOW(),
  ended_at TIMESTAMP,
  
  CONSTRAINT positive_messages CHECK (message_count >= 0)
);

CREATE TABLE chatbot_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES chatbot_conversations(id) ON DELETE CASCADE,
  
  role ENUM('user', 'assistant'),
  content TEXT NOT NULL,
  language VARCHAR(5),                  -- 'en', 'hi', 'ta', 'te'
  
  -- Metadata
  response_type ENUM('predefined', 'rule_based', 'gpt4_api', 'llama_local'),
  confidence_score DECIMAL(3,2),        -- 0.0-1.0 for rule-based responses
  
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Indexes**:
```sql
CREATE INDEX idx_conversations_user_id ON chatbot_conversations(user_id);
CREATE INDEX idx_conversations_date ON chatbot_conversations(created_at DESC);
CREATE INDEX idx_messages_conversation ON chatbot_messages(conversation_id);
CREATE INDEX idx_messages_date ON chatbot_messages(created_at DESC);
```

---

## Entity: `audit_logs`

Privacy & security audit trail.

```sql
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID,
  action VARCHAR(100),                  -- 'resume_uploaded', 'job_applied', 'account_deleted'
  resource_type VARCHAR(100),           -- 'resume', 'application', 'chatbot'
  resource_id VARCHAR(255),
  
  details JSONB,                        -- action-specific data (no sensitive data)
  ip_address INET,
  user_agent TEXT,
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT valid_action CHECK (LENGTH(action) > 0)
);
```

**Indexes**:
```sql
CREATE INDEX idx_audit_user_date ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_date ON audit_logs(created_at DESC);
```

---

## Relationships & Constraints

```
users (1) ──→ (M) resumes
         ──→ (M) recommendations
         ──→ (M) applications
         ──→ (M) chatbot_conversations

job_postings (1) ──→ (M) recommendations
             ──→ (M) applications

skills (1) ──→ (M) resumes (via JSONB)
        ──→ (M) job_postings (via JSONB)
        ──→ (M) recommendations (via JSONB)
```

---

## Key Validation Rules

### Resume Quality Score
```
max_quality = 100
quality = 0
if name AND email: quality += 20
if education populated: quality += 20
if experience populated: quality += 20
if skills.count > 0: quality += 20
if certifications populated: quality += 10
if projects populated: quality += 10
quality = min(quality, 100)
```

### Recommendation Match Percentage
```
semantic_similarity = cosine_similarity(resume_embeddings, job_embeddings)  // 0.0-1.0
keyword_overlap = tf_idf_similarity(resume_skills, job_skills)             // 0.0-1.0
match_percentage = round(
  0.6 * semantic_similarity + 
  0.4 * keyword_overlap
) * 100
```

### Job Posting Expiration
```
job is active while:
  - expiration_date > NOW()
  - is_active = true
  - source still valid (not delisted)

Auto-deactivate after:
  - 30 days since posting_date
  - 90 days since last_seen_date
```

### Resume Auto-Deletion
```
if auto_delete_resume = true AND 
   created_at + resume_retention_days < NOW():
   - delete file from S3
   - mark is_deleted = true
   - soft-delete recommendations, applications
```

---

## Performance Optimization

### Indexes Strategy
- **User lookups**: email (unique), location (filtering)
- **Resume access**: user_id (FK), quality_score (filtering)
- **Job searches**: location, source, posting_date, expiration_date
- **Recommendations**: user_id with created_at (latest first), match_percentage (sorting)
- **Applications**: user_id with applied_at (timeline), status (filtering)

### Query Patterns
```sql
-- Get recommendations for user (top 7 by match score)
SELECT j.*, r.match_percentage, r.explanation_text
FROM recommendations r
JOIN job_postings j ON r.job_id = j.id
WHERE r.user_id = $1 AND j.is_active = true
ORDER BY r.match_percentage DESC
LIMIT 7;

-- Get active applications for user
SELECT a.*, j.title, j.company_name, j.location
FROM applications a
LEFT JOIN job_postings j ON a.job_id = j.id
WHERE a.user_id = $1 AND a.status != 'rejected_by_user'
ORDER BY a.applied_at DESC;

-- Expire old job postings
UPDATE job_postings
SET is_active = false
WHERE is_active = true AND (
  posting_date + INTERVAL '30 days' < NOW() OR
  last_seen_date + INTERVAL '90 days' < NOW()
);
```

---

## Migration Strategy

### Phase 1 (MVP)
- Create all 8 core tables
- Set up indexes for performance-critical queries
- Seed 500-skill taxonomy into `skills` table

### Phase 2
- Add `job_comparison_favorites` table (for comparison feature)
- Add `skill_endorsements` table (for peer validation)
- Partition `audit_logs` by date for archive management

### Phase 3
- Add MongoDB sync for very large job datasets (optional)
- Archive old resumes to S3 (keep minimal metadata in DB)

---

**Data Model Complete** ✅

Ready for implementation: Use SQLAlchemy ORM for Python models, Alembic for migrations, and pytest fixtures for testing.
