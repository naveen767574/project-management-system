# Service Contract: NLP & Recommendation Engine

**Purpose**: Interface contract for resume parsing and job recommendation services  
**Version**: 1.0.0  
**Date**: 2026-02-28

---

## Resume Parser Service

### Purpose
Extract structured information from unstructured resume documents (PDF, DOCX).

### Input Contract

```python
class ResumeParserInput:
    file_path: str              # Path to PDF/DOCX file
    file_content: bytes         # Binary file content
    file_name: str              # Original filename
    extraction_mode: str = "full"  # "full" | "fast" (trade accuracy for speed)
```

### Output Contract

```python
class ParsedResume:
    name: str
    email: str | None
    phone: str | None
    location: str | None
    
    education: list[Education]
    experience: list[Experience]
    skills: list[Skill]
    certifications: list[Certification]
    projects: list[Project]
    
    quality_score: int          # 0-100
    extraction_confidence: float  # 0.0-1.0 (average confidence across fields)
    parsing_time_ms: float
    field_confidence: dict      # per-field confidence scores
    warnings: list[str]         # extraction warnings

class Education:
    degree: str                 # "B.Tech", "Master's", etc.
    field: str                  # "Computer Science"
    institution: str            # "IIT Bombay"
    graduation_year: int | None
    cgpa: float | None
    confidence: float           # 0.0-1.0
    
class Experience:
    company: str
    position: str
    start_date: str             # "2022-06"
    end_date: str | None
    duration_months: int
    description: str
    responsibilities: list[str]
    confidence: float
    
class Skill:
    name: str                   # Normalized to taxonomy
    proficiency: str            # "beginner" | "intermediate" | "expert"
    years_of_experience: float | None
    mentioned_count: int        # How many times skill appears
    confidence: float
    taxonomy_match: bool        # True if in official taxonomy
    
class Certification:
    name: str
    issuer: str | None
    issue_date: str | None
    expiration_date: str | None
    confidence: float
    
class Project:
    name: str
    description: str | None
    url: str | None
    technologies: list[str]
    confidence: float
```

### Error Handling

```python
class ParsingError(Exception):
    code: str                   # "FILE_FORMAT_ERROR" | "PARSING_TIMEOUT" | "INVALID_FILE"
    message: str
    field: str | None           # Which field failed
    recovery_suggestion: str    # User-friendly guidance
```

### Performance SLA
- **Standard Mode** (extraction_mode="full"): <1000ms, ~90% accuracy
- **Fast Mode** (extraction_mode="fast"): <500ms, ~80% accuracy

### Quality Metrics
- **Quality Score Calculation**:
  ```
  quality = 0
  max_quality = 100
  if name present: quality += 15
  if email present: quality += 15
  if education.count >= 1: quality += 15
  if experience.count >= 1: quality += 15
  if skills.count >= 2: quality += 15
  if certifications OR projects present: quality += 10
  quality = min(quality, 100)
  ```

- **Extraction Confidence**: Average of all field confidence scores (per NER model)

---

## Skill Taxonomy Manager

### Purpose
Normalize extracted skills to standard taxonomy (500 curated skills).

### Input Contract

```python
class SkillTaxonomyRequest:
    raw_skills: list[str]       # From resume parsing
    match_threshold: float = 0.7  # Fuzzy match threshold (0-1)
    include_unknown: bool = True   # Keep skills not in taxonomy
```

### Output Contract

```python
class SkillTaxonomyResponse:
    mapped_skills: list[MappedSkill]
    unknown_skills: list[str]
    ambiguous_skills: list[AmbiguousSkill]

class MappedSkill:
    raw_name: str               # From resume
    taxonomy_name: str          # Normalized
    category: str               # "Programming Language" | "Framework" | etc.
    match_confidence: float     # 0.0-1.0
    match_method: str           # "exact" | "fuzzy" | "pattern"
    
class AmbiguousSkill:
    raw_name: str
    potential_matches: list[str]  # Top 3 taxonomy matches
    confidence_scores: list[float]
```

### Taxonomy Categories
- Programming Languages (50 skills)
- Web Frameworks (30)
- Mobile Frameworks (20)
- Databases (25)
- Cloud Platforms (15)
- DevOps/Infrastructure (30)
- Data Science/ML (35)
- Tools & Platforms (80)
- Domain Skills (140)

---

## Recommendation Engine Service

### Purpose
Generate ranked job recommendations matching user resume to available job postings.

### Input Contract

```python
class RecommendationRequest:
    user_id: str
    resume: ParsedResume         # From resume parser
    
    # Filters
    preferred_locations: list[str] | None
    preferred_job_types: list[str] | None  # "internship" | "full-time" | etc.
    min_salary_lpa: float | None
    max_salary_lpa: float | None
    experience_level: str | None  # "fresher" | "associate" | "mid-level" | "senior"
    
    # Config
    limit: int = 7              # Top N recommendations (max 20)
    include_explanations: bool = True
    min_match_threshold: int = 30  # Exclude < 30% matches
```

### Output Contract

```python
class RecommendationResponse:
    user_id: str
    recommendations: list[Recommendation]
    total_jobs_evaluated: int   # For debugging
    generation_time_ms: float
    model_version: str          # For tracking model updates

class Recommendation:
    rank: int                   # 1-7 position
    job_id: str
    job_title: str
    company: str
    location: str
    
    # Matching Scores
    match_percentage: int       # 0-100
    semantic_similarity: float  # 0.0-1.0 (Sentence Transformers)
    keyword_match: float        # 0.0-1.0 (TF-IDF)
    
    # Explanation
    explanation: str            # Human-readable summary
    matched_skills: list[str]   # User's skills found in requirements
    missing_skills: list[str]   # Job requirements user doesn't have
    
    # Job Details
    salary_min_lpa: float | None
    salary_max_lpa: float | None
    job_type: str
    posting_date: str
    source_url: str
    
    # Metadata
    is_remote: bool
    experience_level_required: str
```

### Algorithm

**Step 1: Skill Matching**
```
matched_skills = 0
total_required = 0
for each skill in job.required_skills:
    total_required += 1
    if skill in user.resume.skills:
        matched_skills += 1
        Consider years_of_experience, proficiency level

keyword_match_score = (matched_skills / total_required) * 100  // TF-IDF
```

**Step 2: Semantic Similarity**
```
user_skill_embeddings = sentence_transformers.encode(
    resume.skills_as_text
)  // All skills + experience summary

job_skill_embeddings = sentence_transformers.encode(
    job.required_skills_as_text + job.description
)

semantic_similarity = cosine_similarity(
    user_skill_embeddings,
    job_skill_embeddings
)  // 0.0-1.0
```

**Step 3: Combined Score**
```
match_percentage = round(
    0.6 * semantic_similarity +    // 60% semantic
    0.4 * (keyword_match_score / 100)  // 40% keyword
) * 100
```

**Step 4: Filtering & Ranking**
```
candidates = [all jobs evaluated]
candidates = filter(candidates, match_percentage >= min_threshold)
candidates = filter(candidates, salary in [min, max])
candidates = filter(candidates, location in preferences)
candidates = sort(candidates, match_percentage DESC)
return candidates[0:limit]
```

### Performance SLA
- **Response Time**: <2 seconds for 100 jobs + 7 recommendations
- **Accuracy**: ≥90% human validation of top 3 recommendations
- **Throughput**: ≥100 concurrent recommendation requests

### Evaluation Metrics
```python
class EvaluationMetrics:
    user_clicked_recommendation: bool
    user_applied: bool
    user_bookmarked: bool
    rank_of_application: int        # If user applied (1-7)
    model_accuracy: float           # % of clicked recs / total shown
```

---

## Chatbot Service

### Purpose
Provide intelligent career guidance via conversational interface.

### Input Contract

```python
class ChatbotRequest:
    conversation_id: str | None  # For multi-turn conversations
    message: str                 # User question/input
    language: str = "en"         # "en" | "hi" | "ta" | "te"
    context: dict | None         # Optional: user resume, location, etc.
    response_mode: str = "auto"  # "predefined" | "rule_based" | "gpt4" | "auto"
```

### Output Contract

```python
class ChatbotResponse:
    conversation_id: str         # Unique conversation thread
    message_id: str              # This specific response
    response: str                # Natural language response
    
    # Metadata
    response_type: str           # "predefined" | "rule_based" | "gpt4_api" | "llama_local"
    confidence: float            # 0.0-1.0 (for rule-based)
    response_time_ms: float
    model_version: str
    
    # Control
    suggested_followup: list[str]  # Suggested next questions
    action_required: bool          # Should UI show action button?
    action: dict | None            # {type: "view_jobs", params: {...}}
```

### Knowledge Base Categories

**Rule-Based Q&A Topics** (50 hardcoded pairs):
1. **Skills & Learning** (10 answers)
   - "What skills for data science?"
   - "How to learn Python?"
   - "Which certifications matter?"

2. **Job Search** (12 answers)
   - "How to write good resume?"
   - "How to prepare for interview?"
   - "Salary expectations for fresher?"

3. **Career Planning** (10 answers)
   - "Career path after B.Tech?"
   - "2-year vs 5-year plan?"
   - "How to switch roles?"

4. **Application System** (8 answers)
   - "How to use tracker?"
   - "How to compare jobs?"
   - "How to apply via this platform?"

5. **General Support** (10 answers)
   - "How to upload resume?"
   - "Privacy policy?"
   - "How recommendations work?"

### Performance SLA
- **Response Time**: <500ms (predefined), <1500ms (GPT-4), <2000ms (LLaMA)
- **Accuracy**: ≥85% for rule-based, ≥90% for GPT-4

### Fallback Chain
```
1. Try exact question match in knowledge base
2. Try fuzzy match (Levenshtein distance)
3. Try rule-based extraction + templated response
4. If enabled: Call GPT-4 API
5. If API fails: "I don't have info. Please contact support@..."
```

---

## Error Handling

### Common Errors

```python
class ServiceError(Exception):
    service: str                # "parser" | "recommender" | "chatbot"
    code: str                   # "TIMEOUT" | "MODEL_ERROR" | "NO_DATA"
    message: str
    recovery_action: str        # What user should do
    
class ParseTimeout(ServiceError):
    # Resume parsing >1000ms
    
class RecommendationTimeout(ServiceError):
    # Recommendation generation >2000ms
    
class InsufficientData(ServiceError):
    # User has no resume / job database empty
```

---

## Service Dependencies

- **spaCy**: 3.5+ (NER for education/companies)
- **sentence-transformers**: Latest (semantic similarity)
- **scikit-learn**: Latest (TF-IDF, cosine similarity)
- **Python**: 3.10+
- **FastAPI**: 0.100+
- **PostgreSQL**: 13+

---

## Testing Contract

All services must pass:

1. **Unit Tests**: Input/output contracts validated
2. **Integration Tests**: Services work with PostgreSQL + real data
3. **Accuracy Tests**: Manual validation on 50-resume test set
4. **Performance Tests**: Load testing with 100 concurrent users
5. **Error Tests**: All error paths covered

---

**Service Contract Complete** ✅

Ready for Phase 2 implementation: Backend services implement these interfaces.

