"""SkillPulse: Realistic Indian Job-Postings Generator.
Generates enterprise-grade dataset for Spark RDD classification, prediction, and market intelligence.
Usage: python spark_jobs/generate_data.py [rows]
"""
import csv
import os
import random
import sys

random.seed(42)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 30000

ROLES = {
    # Role: (category, base LPA, core skills, optional skills)
    "Data Scientist": (
        "Data Science", 13.5,
        ["python", "sql", "pandas", "sklearn"],
        ["tensorflow", "pytorch", "spark", "genai", "tableau", "aws"]
    ),
    "Data Analyst": (
        "Business Analytics", 7.5,
        ["sql", "excel", "python"],
        ["tableau", "powerbi", "pandas", "postgresql"]
    ),
    "ML Engineer": (
        "Artificial Intelligence", 16.5,
        ["python", "pytorch", "git"],
        ["tensorflow", "docker", "aws", "genai", "langchain", "kubernetes"]
    ),
    "Data Engineer": (
        "Data Science", 14.0,
        ["python", "sql", "spark"],
        ["hadoop", "aws", "docker", "kubernetes", "postgresql", "azure"]
    ),
    "Frontend Developer": (
        "Software Development", 8.5,
        ["javascript", "react", "git"],
        ["typescript", "figma", "jquery", "angular", "node"]
    ),
    "Backend Developer": (
        "Software Development", 11.0,
        ["java", "sql", "git"],
        ["spring", "docker", "postgresql", "mongodb", "aws", "rust", "node"]
    ),
    "Full Stack Developer": (
        "Software Development", 11.5,
        ["javascript", "react", "node", "sql"],
        ["typescript", "mongodb", "docker", "aws", "git"]
    ),
    "DevOps Engineer": (
        "DevOps", 13.0,
        ["linux", "docker", "git"],
        ["kubernetes", "aws", "azure", "python"]
    ),
    "Cloud Engineer": (
        "Cloud Computing", 13.5,
        ["aws", "linux"],
        ["azure", "docker", "kubernetes", "python"]
    ),
    "Android Developer": (
        "Software Development", 8.5,
        ["kotlin", "java", "git"],
        ["figma", "spring"]
    ),
    "QA Engineer": (
        "Quality Assurance", 6.5,
        ["selenium", "sql"],
        ["java", "python", "git", "jquery"]
    ),
    "AI Application Developer": (
        "Artificial Intelligence", 15.0,
        ["python", "genai", "git"],
        ["langchain", "docker", "aws", "typescript"]
    ),
    "Cybersecurity Analyst": (
        "Cybersecurity", 12.0,
        ["linux", "python", "git"],
        ["aws", "docker", "azure", "sql"]
    ),
}

BONUS = {
    "genai": 4.5, "langchain": 3.5, "rust": 4.0, "kubernetes": 3.0, "spark": 3.0,
    "pytorch": 2.5, "aws": 2.0, "azure": 1.5, "typescript": 1.2, "docker": 1.2,
    "jquery": -1.0, "hadoop": -0.5, "excel": -1.0, "selenium": -0.5
}

GROWTH = {
    "genai": 3.2, "langchain": 4.0, "rust": 1.2, "kubernetes": 0.8, "docker": 0.6,
    "typescript": 0.9, "pytorch": 0.8, "jquery": -0.8, "hadoop": -0.8, "angular": -0.5,
    "selenium": -0.3
}

CITIES = {
    "Bengaluru": 1.20, "Hyderabad": 1.08, "Pune": 1.02, "Chennai": 0.98,
    "Mumbai": 1.15, "Delhi NCR": 1.10, "Kolkata": 0.88, "Mysuru": 0.82, "Kochi": 0.80
}

COMPANIES = [
    # Top Tech / Product
    ("Razorpay", "Fintech", 1.25),
    ("Swiggy", "Consumer Tech", 1.20),
    ("Zomato", "Consumer Tech", 1.18),
    ("Flipkart", "E-Commerce", 1.22),
    ("Microsoft IDC", "Enterprise Tech", 1.35),
    ("Amazon India", "Cloud & Retail", 1.32),
    ("Google India", "Internet", 1.40),
    # IT Services & Consulting
    ("Tata Consultancy Services", "IT Services", 0.90),
    ("Infosys", "IT Services", 0.92),
    ("Wipro", "IT Services", 0.88),
    ("HCL Tech", "IT Services", 0.89),
    # High Growth Startups
    ("Zeta Labs", "Fintech", 1.15),
    ("Orbit Analytics", "Data & AI", 1.12),
    ("Nimbus Tech", "Cloud Solutions", 1.10),
    ("BlueLoom", "EdTech / SaaS", 1.05),
    ("Kaveri Systems", "Enterprise", 1.02),
    ("Greenfield AI", "AI & Research", 1.25),
    ("Pixelwave", "Digital Media", 1.04),
]

LEVELS = {
    "intern": (0.35, 0.15),   # (multiplier, probability weight)
    "junior": (0.80, 0.35),
    "mid": (1.25, 0.30),
    "senior": (1.85, 0.20)
}

WORK_MODES = [("Hybrid", 0.50), ("Remote", 0.28), ("Onsite", 0.22)]
EMP_TYPES = [("Full-time", 0.80), ("Internship", 0.14), ("Contract", 0.06)]
MONTHS = [f"{y}-{m:02d}" for y in (2024, 2025) for m in range(1, 13)]

INTRO = [
    "We are seeking a talented {t} to join {c}.",
    "Exciting opening for a passionate {t} at {c}.",
    "Grow your career at {c} as our new {t}.",
    "{c} is looking for an experienced and driven {t}."
]

BODY = [
    "You will develop core services using {s}.",
    "Hands-on experience with {s} is required for this role.",
    "Our tech stack heavily leverages {s}.",
    "Strong technical expertise in {s} is essential.",
    "Key responsibilities include designing scalable systems with {s}."
]

FILL = [
    "Collaborate with cross-functional teams to build resilient architectures.",
    "Write clean, well-tested, maintainable code following agile best practices.",
    "Own product features end-to-end from requirement to production deployment.",
    "Opportunity to work in a high-impact engineering culture with strong mentorship."
]

rows = []
for i in range(N):
    t, (cat, base, core, opt) = random.choice(list(ROLES.items()))
    mi = random.randrange(24)
    month = MONTHS[mi]
    
    lvl = random.choices(list(LEVELS), [v[1] for v in LEVELS.values()])[0]
    
    # Select skills
    sk = {s for s in core if random.random() < 0.90}
    for s in opt:
        p = 0.35 * max(0.05, 1.0 + GROWTH.get(s, 0.0) * mi / 23.0)
        if random.random() < min(p, 0.92):
            sk.add(s)
    if not sk:
        sk.add(core[0])
        
    city = random.choice(list(CITIES))
    company_info = random.choice(COMPANIES)
    company, industry, company_mult = company_info
    
    work_mode = random.choices([w[0] for w in WORK_MODES], [w[1] for w in WORK_MODES])[0]
    emp_type = "Internship" if lvl == "intern" else random.choices([e[0] for e in EMP_TYPES], [e[1] for e in EMP_TYPES])[0]
    
    skill_bonus = sum(BONUS.get(s, 0.0) for s in sk)
    lpa = (base + skill_bonus) * LEVELS[lvl][0] * CITIES[city] * company_mult * random.uniform(0.92, 1.08)
    lpa = max(2.8, round(lpa, 2))
    
    skill_list = list(sk)
    random.shuffle(skill_list)
    desc = " ".join([
        random.choice(INTRO).format(t=t, c=company),
        random.choice(BODY).format(s=", ".join(skill_list)),
        random.choice(FILL)
    ])
    
    rows.append([
        i + 1, t, cat, company, city, month, lvl, work_mode, emp_type, lpa, desc
    ])

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(out_dir, exist_ok=True)
csv_path = os.path.join(out_dir, "job_postings.csv")

header = [
    "job_id", "title", "category", "company", "city", "month",
    "experience", "work_mode", "employment_type", "salary_lpa", "description"
]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Successfully wrote {len(rows)} enterprise job postings -> {csv_path}")
