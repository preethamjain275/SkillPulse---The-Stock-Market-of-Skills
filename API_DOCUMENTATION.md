# API DOCUMENTATION: SkillPulse REST Services

Base URL: `http://127.0.0.1:8000/api`  
Interactive Swagger UI: `http://127.0.0.1:8000/docs`  
ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 1. System Endpoints

### `GET /api/health`
Returns the operational health and Spark engine status.
- **Response 200 OK:**
  ```json
  {
    "status": "healthy",
    "service": "SkillPulse Job Market Analytics API",
    "version": "2.0.0",
    "postings_loaded": 30000,
    "spark_engine": "SparkRDD-Native (Zero-JVM Fault-Tolerant Engine)"
  }
  ```

---

## 2. Market Intelligence Endpoints

### `GET /api/dashboard/overview`
Retrieves top-level KPIs, distributions, and top demanded entities.
- **Response 200 OK:** Returns metadata, work_mode distribution, experience breakdown, top skills, top roles, and co-occurring skill pairs.

### `GET /api/skills`
Retrieves all technical skills with financial indicators.
- **Query Parameters:**
  - `status` (string, optional): `All`, `Rising`, `Stable`, `Falling`
  - `sort_by` (string, default: `demand_index`): `demand_index`, `momentum`, `premium`, `avg_lpa`, `name`
  - `limit` (integer, default: `50`)

### `GET /api/skills/trends`
Retrieves 24-month progression time-series for all monitored technologies.

---

## 3. Machine Learning & Inference Endpoints

### `POST /api/classification/predict`
Classifies candidate skill profile into a discrete salary band (`Low`, `Mid`, `High`) using Naive Bayes trained on Spark RDDs.
- **Request Body:**
  ```json
  {
    "skills": ["python", "pytorch", "genai"],
    "experience": "senior",
    "category": "Artificial Intelligence"
  }
  ```
- **Response 200 OK:**
  ```json
  {
    "predicted_band": "High",
    "band_probabilities": {
      "Low": 0.0,
      "Mid": 1.9,
      "High": 98.1
    },
    "confidence": 98.1,
    "features_used": ["sk_python", "sk_pytorch", "sk_genai", "lvl_senior", "cat_Artificial Intelligence"],
    "disclaimer": "Predicted using Naive Bayes classifier trained on 30,000 job postings via Apache Spark RDD transformations with Laplace smoothing."
  }
  ```

### `POST /api/salary/predict`
Calculates estimated compensation range based on role, skills, experience, and city cost factor.
- **Request Body:**
  ```json
  {
    "role": "Data Scientist",
    "skills": ["python", "pandas", "sklearn"],
    "experience": "junior",
    "city": "Bengaluru"
  }
  ```
- **Response 200 OK:** Returns `estimated_lpa_min`, `estimated_lpa_median`, `estimated_lpa_max`, `predicted_band`, and `city_factor`.

---

## 4. Career Planning & Assistance Endpoints

### `POST /api/skill-gap/analyze`
Evaluates user skills against target role requirements and outputs prioritized missing skills.
- **Request Body:**
  ```json
  {
    "current_skills": ["python", "sql"],
    "target_role": "Data Scientist",
    "experience": "junior"
  }
  ```
- **Response 200 OK:** Returns `match_percentage`, `possessed_skills`, and `missing_skills` array with frequency percentage and priority.

### `POST /api/career-roadmap/generate`
Generates a phased learning roadmap with time estimates, project capstones, and free resources.

### `POST /api/career-readiness/analyze`
Computes an empirical readiness score (0–100) with a transparent formula breakdown.

### `POST /api/career-assistant/chat`
Answers natural language career questions grounded directly in real dataset analytics.
- **Request Body:**
  ```json
  {
    "message": "Which skills have rising demand?"
  }
  ```

---

## 5. Jobs & Entity Intelligence

### `GET /api/jobs`
Query filtered job postings from database with pagination.
- **Query Parameters:** `city`, `role`, `company`, `experience`, `work_mode`, `min_salary`, `page`, `page_size`.

### `GET /api/jobs/freshers`
Convenience endpoint returning only junior and internship positions.

### `GET /api/companies` and `GET /api/companies/{company_name}`
Company-level analytics, work-mode breakdown, and demanded skills.

### `GET /api/locations`
Location salary benchmarks and posting concentrations.
