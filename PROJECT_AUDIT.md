# PROJECT AUDIT: SkillPulse
**Project:** Job Market Data Analytics: A Spark RDD Approach to Classification and Prediction  
**Product Title:** SkillPulse – The Stock Market of Skills  
**Audit Timestamp:** 2026-11-10T00:40:00+05:30  
**Auditor:** Senior Software Architect & Lead Engineer  

---

## 1. Executive Summary

An exhaustive inspection and live runtime evaluation of the existing SkillPulse codebase was performed. 

The original codebase consisted of a lightweight prototype:
1. A synthetic data generator script (`spark_jobs/generate_data.py`) creating ~30,000 job postings with basic attributes (`title, city, month, experience, salary_lpa, description`).
2. A single PySpark script (`spark_jobs/pipeline.py`) that uses RDD transformations (`map`, `flatMap`, `reduceByKey`, `aggregateByKey`, `randomSplit`) to train a custom Naive Bayes salary-band classifier and compute 24-month linear trend slopes.
3. A static frontend prototype (`frontend/index.html`, `style.css`, `app.js`) that renders precomputed stats from `frontend/data/insights.js` without any backend server or API communication.
4. **No FastAPI backend**, **no React architecture**, **no persistent database**, **no comprehensive metrics (precision, recall, F1)**, and **no interactive real-time multi-dimensional filters**.

---

## 2. Component-by-Component Audit

| Component | Status | Existing Implementation | Required Action |
|---|---|---|---|
| **Spark RDD Pipeline** | PARTIALLY IMPLEMENTED | `spark_jobs/pipeline.py` implements basic RDD transformations (`map`, `flatMap`, `filter`, `reduceByKey`, `aggregateByKey`, `randomSplit`) for salary-band Naive Bayes and 24-month trend slope. Lacks multi-label classification, precision/recall/F1 calculation, and job category extraction. | Refactor into modular Spark RDD architecture (`ingestion`, `preprocessing`, `classification`, `trend_analysis`, `evaluation`). Provide dual runtime capability (PySpark RDD + native standalone Spark RDD executor) to guarantee 100% resilient execution across environments. |
| **Dataset Import** | PARTIALLY IMPLEMENTED | `spark_jobs/generate_data.py` generates 30,000 records. Missing critical enterprise fields required by the spec: company name, work mode (remote/hybrid/onsite), employment type, education level, and job category. | Enhance the data generator and ingestion pipeline with realistic Indian market schema (e.g. tier-1/tier-2 tech hubs, leading IT & product companies, diverse roles, and rich work modes). |
| **Data Cleaning** | PARTIALLY IMPLEMENTED | Elementary regex tokenization in `parse()` function. Drops records missing salary or with zero extracted skills. | Build dedicated data cleaning & normalization pipeline: handling text normalisation, salary bounds validation, skill alias mapping, location canonicalization, and deduplication. |
| **Classification** | PARTIALLY IMPLEMENTED | Custom Naive Bayes written with Spark RDDs classifying records into 3 salary bands (`Low`, `Mid`, `High`). Currently outputs only raw accuracy and confusion counts. | Implement complete evaluation metrics (Accuracy, Precision, Recall, F1-Score per band and macro-average), model evaluation dashboard, and expand to job categories and experience levels. |
| **Prediction** | PARTIALLY IMPLEMENTED | Only client-side JavaScript probability multiplication against precomputed band averages in `app.js`. No backend inference. | Develop robust statistical salary prediction engine with minimum, median, and maximum salary estimation based on role, skills, experience, and city cost factor with clear statistical disclaimers. |
| **Skill Gap Analyzer** | PARTIALLY IMPLEMENTED | Minimal client-side JavaScript prototype calculating overlap between selected skills and top 4 missing skills. | Build full-fledged Skill Gap Intelligence module: prioritized missing skills by market frequency and salary premium, optimal learning sequence, and downloadable career report. |
| **FastAPI Backend** | NOT IMPLEMENTED | No backend existed. The project was previously served via Python's static HTTP server (`http.server`). | Develop comprehensive FastAPI backend with modular API routers, Pydantic schemas, input validation, CORS, error boundaries, and endpoints for all 12 modules. |
| **React Frontend** | NOT IMPLEMENTED | Exists only as a vanilla HTML/JS/CSS prototype without a modern component structure or state management. | Build a modern, modular, component-driven frontend with React, Tailwind CSS, Lucide icons, responsive navigation, and Recharts/interactive data visualizations. |
| **Dashboard** | PARTIALLY IMPLEMENTED | Displays 4 static KPIs and a small table from static precomputed JSON. Lacks dynamic filtering or cross-dimensional analysis. | Create a comprehensive Job Market Intelligence dashboard with interactive multi-filter controls (Role, City, Company, Work Mode, Experience, Skill) and dynamic KPI recalculation. |
| **Charts and Visualizations** | PARTIALLY IMPLEMENTED | Basic inline SVG polyline sparklines and CSS progress bars. Lacks interactive tooltips, time-series zoom, or multi-metric comparison. | Implement interactive, responsive visual charts: multi-line skill trend charts, salary distribution bars, role radar/bar comparisons, city geo-charts, and confusion matrix heatmaps. |
| **Database** | NOT IMPLEMENTED | Flat CSV and JSON files only. | Implement structured data persistence and caching layer using SQLite / Parquet / indexed JSON for fast queries and offline resilience. |
| **Mobile Responsiveness** | NEEDS IMPROVEMENT | Elementary media queries in `style.css`. Tables overflow on mobile viewports; navigation lacks a mobile drawer. | Implement mobile-first responsive layout with collapsible sidebar, touch-optimized chips, readable mobile card tables, and adaptive chart scaling. |
| **Documentation** | NEEDS IMPROVEMENT | Brief 30-line `README.md`. No architectural diagrams, methodology explanations, audit reports, or installation manuals. | Author a comprehensive documentation suite (PROJECT_AUDIT, PROJECT_ARCHITECTURE, PROBLEM_STATEMENT, METHODOLOGY, DATASET_DOCUMENTATION, API_DOCUMENTATION, INSTALLATION_GUIDE, TESTING_REPORT, FUTURE_SCOPE). |

---

## 3. Verification & Runtime Testing Details

1. **Python Environment Verification:**
   - Python: 3.13.13 (64-bit)
   - Packages installed: FastAPI 0.141.1, Uvicorn 0.54.0, Pydantic 2.13.5, NumPy 2.5.3, PyTest 9.1.1.
   - Node.js: v24.10.0, npm: 11.6.1.
2. **Data Generation Execution:**
   - Tested running `python spark_jobs/generate_data.py 30000`. Successfully generated 30,000 rows (`5.5 MB`) in `data/job_postings.csv`.
3. **Pipeline Execution:**
   - Previous `spark_jobs/pipeline.py` requires PySpark. When run without PySpark installed or on JVM incompatibilities, the pipeline throws `ModuleNotFoundError: No module named 'pyspark'`.
4. **Frontend Serving:**
   - Tested `http.server` on port 8000. Verified HTTP 200 response and browser rendering of the static prototype.
   - Identified that none of the forms or interactive cards query a live backend API.

---

## 4. Next Implementation Actions

1. **Phase 1: Data Engineering & Spark RDD Engine**
   - Expand `generate_data.py` with companies, work modes (remote/hybrid/onsite), and job categories.
   - Construct robust Spark RDD pipeline with both PySpark and zero-dependency standalone RDD executor ensuring verifiable RDD transformations (`map`, `flatMap`, `reduceByKey`, `aggregateByKey`, etc.).
   - Calculate precision, recall, F1, full confusion matrix, and skill momentum indices.
2. **Phase 2: FastAPI Backend Architecture**
   - Build FastAPI server in `backend/` with structured routes:
     - `/api/dashboard/overview`
     - `/api/skills` (trends, top-demanded, rising, declining)
     - `/api/classification/predict` (Naive Bayes inference)
     - `/api/salary/predict`
     - `/api/skill-gap/analyze`
     - `/api/career-roadmap/generate`
     - `/api/jobs` and `/api/jobs/freshers`
     - `/api/companies` and `/api/companies/{company_id}`
     - `/api/locations`
     - `/api/career-readiness/analyze`
     - `/api/career-assistant/chat`
     - `/api/model/evaluation`
     - `/api/dataset/summary`
3. **Phase 3: React & Tailwind Frontend Application**
   - Implement complete 12-module frontend with clean SaaS light theme: Navy Blue (`#0f172a`), Royal Blue (`#2563eb`), Off-white (`#f8fafc`), Teal (`#0d9488`), and emerald/rose indicators.
   - Reusable UI components, interactive charts, desktop sidebar, and responsive mobile navigation.
4. **Phase 4: Comprehensive Testing & Verification**
   - Unit tests for backend endpoints and RDD computations.
   - End-to-end verification of all interactive features.
5. **Phase 5: Documentation Suite & Final Artifact Packaging**
   - Generate all 10 required markdown documents and final deployable archive.
