# FUTURE SCOPE & ENHANCEMENTS: SkillPulse

## 1. Automated Real-Time Job Scraping & Ingestion
- **Current State:** Ingests standardized batches of 30,000 postings from CSV files.
- **Future Scope:** Integrate automated web scraping pipelines (LinkedIn Public Job Feed, Naukri, Indeed RSS) scheduled via Apache Airflow to continuously append daily employment trends into partitioned storage.

---

## 2. Advanced Big Data Infrastructure
- **Distributed Cluster Deployment:** Transition local master execution (`local[*]`) to an elastic Amazon EMR or Databricks cluster processing millions of global postings across multiple worker nodes.
- **Delta Lake Integration:** Introduce Delta Lake / Apache Iceberg ACID transactions for time-travel queries and incremental skill momentum tracking over 5–10 year longitudinal horizons.

---

## 3. Natural Language Processing & Deep Learning
- **Semantic Transformer Embeddings:** Augment canonical keyword extraction with BERT / RoBERTa domain embeddings to identify emerging synonyms and composite tools automatically.
- **Resume PDF Parser:** Add direct student resume upload (PDF/DOCX) that automatically extracts candidate skills and runs the Skill Gap Analyzer and Readiness Assessment in one click.

---

## 4. Enterprise & College Placement Portal
- **University Analytics Dashboard:** Enable college placement cells to upload batches of student profiles to identify aggregate batch weaknesses (e.g. "45% of students lack Git and Docker proficiency before campus hiring season").
- **Direct Employer Pipeline:** Connect verified student readiness scores with hiring partners for pre-screened campus interviews.
