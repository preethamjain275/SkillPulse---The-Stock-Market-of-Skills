# DATASET DOCUMENTATION: SkillPulse

## 1. Dataset Overview
- **File Name:** `data/job_postings.csv`
- **Total Records:** 30,000 postings
- **Size:** ~5.5 MB
- **Coverage Period:** 24 Months (January 2024 to December 2025)
- **Domain:** Indian Information Technology, Product Companies, and Fintech Ecosystem

---

## 2. Schema Specification

| Column | Type | Description | Sample Values |
|---|---|---|---|
| `job_id` | Integer | Unique identifier for each posting | `1`, `42`, `30000` |
| `title` | String | Target role title | `Data Scientist`, `ML Engineer`, `Full Stack Developer` |
| `category` | String | Broad career classification | `Software Development`, `Data Science`, `Artificial Intelligence`, `Cloud Computing`, `DevOps`, `Cybersecurity`, `Quality Assurance`, `Business Analytics` |
| `company` | String | Hiring company name | `Razorpay`, `Swiggy`, `TCS`, `Infosys`, `Microsoft IDC`, `Google India` |
| `city` | String | Indian tech hub location | `Bengaluru`, `Hyderabad`, `Pune`, `Mumbai`, `Delhi NCR`, `Chennai`, `Kolkata`, `Mysuru`, `Kochi` |
| `month` | String | Publication date (YYYY-MM) | `2024-01` through `2025-12` |
| `experience` | String | Seniority tier | `intern`, `junior`, `mid`, `senior` |
| `work_mode` | String | Workplace flexibility | `Hybrid`, `Remote`, `Onsite` |
| `employment_type` | String | Contractual structure | `Full-time`, `Internship`, `Contract` |
| `salary_lpa` | Float | Advertised salary in Lakhs Per Annum (LPA) | `6.50`, `18.25`, `42.00` |
| `description` | Text | Job description text containing required tech stack | `"We are seeking a talented Data Scientist at Razorpay. Hands-on experience with python, sql, pandas, sklearn is required..."` |

---

## 3. Canonical Technical Skills (33 Monitored Technologies)

1. **Languages:** Python, Java, JavaScript, TypeScript, Rust, Kotlin
2. **Databases & Data Storage:** SQL, PostgreSQL, MongoDB
3. **Frontend & Mobile:** React, Angular, jQuery, Figma
4. **Backend & Enterprise:** Node.js, Spring Boot
5. **Data Engineering & Big Data:** Apache Spark, Hadoop, Pandas
6. **Data Science & ML:** Scikit-Learn, TensorFlow, PyTorch
7. **Generative AI & LLMs:** Generative AI, LangChain
8. **Cloud & Infrastructure:** AWS, Azure, Docker, Kubernetes, Linux, Git
9. **Business Intelligence & Testing:** Tableau, Power BI, Excel, Selenium

---

## 4. Synthetic Generation Methodology & Grounding
The dataset is generated via `spark_jobs/generate_data.py` grounded in published compensation and demand ranges from Indian tech market surveys (Nasscom, LinkedIn Economic Graph, and Glassdoor):
- **Base Salaries:** Aligned with Indian market standards (e.g. QA Engineer base ₹6.5L, ML Engineer base ₹16.5L).
- **Skill Premiums:** Applied realistic compounding premiums for scarce skills (GenAI +₹4.5L, LangChain +₹3.5L, Rust +₹4.0L).
- **City Cost Index:** Bengaluru (1.20x), Mumbai (1.15x), Delhi NCR (1.10x), Hyderabad (1.08x), Pune (1.02x), Kolkata (0.88x), Mysuru (0.82x), Kochi (0.80x).
- **Experience Multipliers:** Intern (0.35x), Junior (0.80x), Mid (1.25x), Senior (1.85x).
