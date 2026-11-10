# INSTALLATION & EXECUTION GUIDE: SkillPulse

This guide provides step-by-step instructions to install, execute, and verify the complete SkillPulse platform on Windows, macOS, or Linux.

---

## 1. Environment Requirements
- **Python:** 3.10, 3.11, 3.12, or 3.13 (Tested on Python 3.13)
- **Web Browser:** Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari
- **Java (Optional for PySpark cluster execution):** Java 11, 17, or 21.  
  *(Note: A built-in zero-JVM Spark RDD engine is bundled, allowing full execution even if Java is not installed or configured on the machine).*

---

## 2. Step-by-Step Installation

### Step 1: Clone or Navigate to Project
```bash
cd skillpulse
```

### Step 2: Create and Activate Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```
*Dependencies included: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `numpy`, `pytest`, `pyspark`.*

---

## 3. Execution Options

### Option A: Launch Full Full-Stack Platform (FastAPI + React Frontend)
Run the uvicorn development server:
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Once launched, navigate to:
- **Web Dashboard:** [http://localhost:8000/](http://localhost:8000/)
- **Interactive API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Option B: Run the Spark Analytical Pipeline Manually
To re-run the distributed Spark RDD processing from the command line:
```bash
python spark_jobs/pipeline.py
```
Outputs are automatically written to `frontend/data/insights.json` and `frontend/data/insights.js`.

### Option C: Re-generate Synthetic Job Postings
```bash
python spark_jobs/generate_data.py 30000
```

---

## 4. Running the Automated Test Suite
To verify that all backend routes, ML models, and analytics function correctly:
```bash
pytest backend/tests/test_api.py -v
```
All 10 test cases should pass in ~1.5 seconds.

---

## 5. Troubleshooting & FAQ

- **Error: `Address already in use (port 8000)`**  
  If port 8000 is occupied by another process, run on another port:
  ```bash
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload
  ```
- **Does it work completely offline?**  
  Yes! The frontend includes precomputed analytics in `frontend/data/insights.js` and pure-Python logic so all dashboards and tools function even when disconnected from the internet.
