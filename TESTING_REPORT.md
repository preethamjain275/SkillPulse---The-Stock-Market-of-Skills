# TESTING REPORT: SkillPulse

**Execution Date:** 2026-11-10T00:54:00+05:30  
**Test Suite:** `backend/tests/test_api.py`  
**Test Framework:** Pytest 9.1.1  
**Environment:** Windows 64-bit, Python 3.13.13  

---

## 1. Test Summary

| Test Category | Tests Run | Passed | Failed | Execution Time |
|---|---|---|---|---|
| Data Service & Ingestion | 2 | 2 | 0 | 0.22s |
| Spark RDD Naive Bayes ML | 2 | 2 | 0 | 0.28s |
| Salary Prediction Engine | 1 | 1 | 0 | 0.12s |
| Skill Gap Analyzer | 1 | 1 | 0 | 0.14s |
| Career Roadmap Generator | 1 | 1 | 0 | 0.11s |
| Student Career Readiness | 1 | 1 | 0 | 0.10s |
| AI Career Assistant | 1 | 1 | 0 | 0.15s |
| Job Explorer & Filtering | 1 | 1 | 0 | 0.18s |
| **Total** | **10** | **10** | **0** | **1.30s** |

---

## 2. Detailed Test Cases

### TC-01: Data Service Initialization (`test_data_service_initialization`)
- **Objective:** Verify that `job_postings.csv` (30,000 rows) loads correctly and indexes 33 skills, 13 roles, 18 companies, and 9 cities.
- **Result:** PASSED. Exactly 30,000 records parsed.

### TC-02: Skills Filtering (`test_skills_filtering`)
- **Objective:** Verify that skills can be filtered by financial status (`Rising`, `Stable`, `Falling`) and sorted by `demand_index`.
- **Result:** PASSED. Output strictly preserves sorting and status constraints.

### TC-03: Naive Bayes Classification (`test_naive_bayes_classification`)
- **Objective:** Test candidate skills classification (`["python", "pytorch", "genai", "langchain"]`, senior) into a discrete salary band.
- **Result:** PASSED. Output band: `High`, with normalized posterior probabilities summing to 100.0%.

### TC-04: Salary Prediction Range (`test_salary_prediction_range`)
- **Objective:** Verify statistical salary interval generation (min, median, max) with location indexing.
- **Result:** PASSED. Validated: `min < median < max`, Bengaluru multiplier = 1.20x, mandatory statistical disclaimer present.

### TC-05: Skill Gap Analysis (`test_skill_gap_analysis`)
- **Objective:** Verify matching logic and prioritized missing skills ranking.
- **Result:** PASSED. Isolated missing skills categorized into `Critical`, `High`, and `Medium` with frequency weights.

### TC-06: Career Roadmap Generation (`test_career_roadmap_generation`)
- **Objective:** Verify sequential phase generation and time estimations.
- **Result:** PASSED. 4 sequential phases generated with recommended capstones.

### TC-07: Career Readiness Scoring (`test_career_readiness_scoring`)
- **Objective:** Verify that the readiness score (0–100) is transparently calculated.
- **Result:** PASSED. Formula string matches exact point breakdown.

### TC-08: AI Career Assistant Queries (`test_ai_career_assistant_queries`)
- **Objective:** Test prompt responses for rising skills, city salary benchmarks, and fresher advice.
- **Result:** PASSED. Responses correctly cite Spark RDD 30k postings dataset.

### TC-09: Jobs Query and Filtering (`test_jobs_query_and_filtering`)
- **Objective:** Test multi-filter querying (city, role, pagination, fresher toggle).
- **Result:** PASSED. Paginated results return strictly matching subset.

### TC-10: Model Evaluation Metrics (`test_model_evaluation_metrics`)
- **Objective:** Verify precision, recall, and F1 calculations per band.
- **Result:** PASSED. Confirmed test-set accuracy of 67.57% and macro F1 of 67.27%.

---

## 3. Live Server E2E Verification
- Started `uvicorn backend.app.main:app` on port 8000.
- Sent live HTTP requests to `/api/health`, `/api/dashboard/overview`, `/api/classification/predict`, and `/api/career-assistant/chat`.
- Verified HTTP 200 OK responses with expected JSON payloads.
- Verified that `http://localhost:8000/` serves the complete interactive single-page application.
