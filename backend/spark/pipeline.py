"""SkillPulse Spark RDD Analytical & Machine Learning Pipeline.
Implements data ingestion, preprocessing, Naive Bayes classification from scratch,
model evaluation (Accuracy, Precision, Recall, F1), trend regression, skill stock market indices,
role profiling, company intelligence, and co-occurring skill-pair mining.

Strictly adheres to Spark RDD transformations and actions:
map, flatMap, filter, reduceByKey, aggregateByKey, groupByKey, sortBy, distinct,
count, collect, take, takeOrdered, cache, broadcast.
"""
from __future__ import annotations
import csv
import json
import math
import os
import re
import sys
import time
from itertools import combinations
from operator import add
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# Dynamically support PySpark when JVM is compatible, else robust Spark RDD Engine
USE_PYSPARK = False
try:
    if os.environ.get("FORCE_RDD_ENGINE") != "1":
        from pyspark.sql import SparkSession
        import pyspark
        USE_PYSPARK = True
except Exception:
    USE_PYSPARK = False

from backend.spark.rdd_engine import SparkContext, Broadcast, RDD

SKILLS_CANONICAL = [
    "python", "java", "javascript", "typescript", "sql", "react", "angular", "jquery",
    "node", "spring", "docker", "kubernetes", "aws", "azure", "git", "linux", "spark",
    "hadoop", "pandas", "sklearn", "tensorflow", "pytorch", "genai", "langchain",
    "tableau", "powerbi", "excel", "mongodb", "postgresql", "figma", "selenium",
    "rust", "kotlin"
]

ROLES_LIST = [
    "Data Scientist", "Data Analyst", "ML Engineer", "Data Engineer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "DevOps Engineer", "Cloud Engineer", "Android Developer",
    "QA Engineer", "AI Application Developer", "Cybersecurity Analyst"
]

CITIES_LIST = [
    "Bengaluru", "Hyderabad", "Pune", "Chennai", "Mumbai",
    "Delhi NCR", "Kolkata", "Mysuru", "Kochi"
]


def slope_percentage(series: List[float]) -> float:
    """Least-squares slope as % change of mean per month."""
    n = len(series)
    if n <= 1:
        return 0.0
    mean_x = (n - 1) / 2.0
    mean_y = sum(series) / n
    denom = sum((i - mean_x) ** 2 for i in range(n)) or 1.0
    num = sum((i - mean_x) * (y - mean_y) for i, y in enumerate(series))
    return round((num / denom) / (mean_y or 1.0) * 100.0, 2)


def variance(values: List[float]) -> float:
    """Calculates sample variance for demand volatility."""
    n = len(values)
    if n <= 1:
        return 0.0
    avg = sum(values) / n
    return round(math.sqrt(sum((x - avg) ** 2 for x in values) / (n - 1)), 2)


def band_of(lpa: float) -> str:
    """Discretizes continuous salary LPA into 3 discrete target bands."""
    if lpa < 8.0:
        return "Low"
    elif lpa < 18.0:
        return "Mid"
    return "High"


def run_pipeline(
    data_csv_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    force_engine: bool = False
) -> Dict[str, Any]:
    """Executes the full distributed Spark RDD analytical pipeline."""
    start_time = time.time()
    
    if data_csv_path is None:
        data_csv_path = os.path.join(ROOT_DIR, "data", "job_postings.csv")
    if output_dir is None:
        output_dir = os.path.join(ROOT_DIR, "frontend", "data")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Initialize Spark Context / Session
    sc = None
    spark = None
    active_engine = "SparkRDD-Native"
    
    if USE_PYSPARK and not force_engine:
        try:
            spark = SparkSession.builder \
                .appName("SkillPulse-Analytics") \
                .master("local[*]") \
                .config("spark.driver.memory", "2g") \
                .getOrCreate()
            sc = spark.sparkContext
            sc.setLogLevel("ERROR")
            active_engine = "PySpark-v" + str(pyspark.__version__)
        except Exception:
            sc = None

    if sc is None:
        sc = SparkContext(master="local[*]", appName="SkillPulse-NativeRDD")
        active_engine = "SparkRDD-Native (Zero-JVM Fault-Tolerant Engine)"

    # Broadcast Skills lexicon
    skills_broadcast = sc.broadcast(set(SKILLS_CANONICAL))

    # 2. Ingestion & RDD Creation
    rows = []
    with open(data_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    # Parallelize dataset into distributed RDD partitions
    raw_rdd = sc.parallelize(rows, numSlices=4)

    # 3. Data Cleaning & Feature Extraction (map & filter transformations)
    def parse_job_record(r: Dict[str, str]) -> Optional[Dict[str, Any]]:
        try:
            lpa = float(r.get("salary_lpa", 0))
            if lpa <= 0:
                return None
        except (ValueError, TypeError):
            return None

        desc = (r.get("description") or "").lower()
        tokens = {t.strip(".") for t in re.findall(r"[a-z][a-z+#.]*", desc)}
        extracted_skills = sorted(tokens & skills_broadcast.value)
        if not extracted_skills:
            return None

        exp = (r.get("experience") or "junior").strip().lower()
        company = (r.get("company") or "Tech Corp").strip()
        category = (r.get("category") or "Software Development").strip()
        work_mode = (r.get("work_mode") or "Hybrid").strip()
        emp_type = (r.get("employment_type") or "Full-time").strip()
        city = (r.get("city") or "Bengaluru").strip()
        title = (r.get("title") or "Software Engineer").strip()
        month = (r.get("month") or "2024-01").strip()

        # Feature representations for Naive Bayes classification
        features = (
            [f"sk_{s}" for s in extracted_skills] +
            [f"lvl_{exp}"] +
            [f"cat_{category}"] +
            [f"mode_{work_mode}"]
        )

        return {
            "job_id": r.get("job_id", ""),
            "title": title,
            "category": category,
            "company": company,
            "city": city,
            "month": month,
            "experience": exp,
            "work_mode": work_mode,
            "employment_type": emp_type,
            "salary_lpa": lpa,
            "band": band_of(lpa),
            "skills": extracted_skills,
            "features": features
        }

    # Transform: map then filter bad rows, then cache in memory
    jobs_rdd = raw_rdd.map(parse_job_record).filter(lambda x: x is not None).cache()
    total_postings = jobs_rdd.count()
    if total_postings == 0:
        raise ValueError("No valid job postings after cleaning!")

    add_tuple = (lambda a, v: (a[0] + v, a[1] + 1), lambda a, b: (a[0] + b[0], a[1] + b[1]))

    # 4. Naive Bayes Classification with Train/Test Split (randomSplit, reduceByKey, broadcast)
    train_rdd, test_rdd = jobs_rdd.randomSplit([0.80, 0.20], seed=42)
    
    # Class priors: count of documents per band
    class_counts = train_rdd.map(lambda j: (j["band"], 1)).reduceByKey(add).collectAsMap()
    total_train = sum(class_counts.values())

    # Feature likelihoods: count of feature occurrences per band
    feature_counts = train_rdd.flatMap(
        lambda j: [((j["band"], f), 1) for f in j["features"]]
    ).reduceByKey(add).collectAsMap()

    # Broadcast trained model parameters to worker nodes
    model_broadcast = sc.broadcast((class_counts, feature_counts, total_train))

    def predict_band(features: List[str]) -> Tuple[str, Dict[str, float]]:
        c_cnt, f_cnt, t_train = model_broadcast.value
        log_probs = {}
        for c, count in c_cnt.items():
            # Log prior with Laplace smoothing
            lp = math.log((count + 1.0) / (t_train + len(c_cnt)))
            # Log likelihoods
            for feat in features:
                f_c = f_cnt.get((c, feat), 0)
                lp += math.log((f_c + 1.0) / (count + 2.0))
            log_probs[c] = lp

        # Softmax for normalized posterior probabilities
        max_lp = max(log_probs.values())
        exp_vals = {c: math.exp(lp - max_lp) for c, lp in log_probs.items()}
        sum_exp = sum(exp_vals.values()) or 1.0
        posteriors = {c: exp_vals[c] / sum_exp for c in exp_vals}
        predicted_class = max(posteriors, key=posteriors.get)
        return predicted_class, posteriors

    # Evaluate on unseen test partition
    test_predictions = test_rdd.map(
        lambda j: (j["band"], predict_band(j["features"])[0])
    )
    confusion_counts = test_predictions.map(lambda pair: (pair, 1)).reduceByKey(add).collectAsMap()

    # Calculate Accuracy, Precision, Recall, F1
    bands = ["Low", "Mid", "High"]
    metrics_per_band = {}
    total_test = sum(confusion_counts.values()) or 1
    total_correct = sum(v for (a, p), v in confusion_counts.items() if a == p)
    overall_accuracy = round(total_correct / total_test * 100.0, 2)

    for b in bands:
        tp = confusion_counts.get((b, b), 0)
        fp = sum(v for (a, p), v in confusion_counts.items() if p == b and a != b)
        fn = sum(v for (a, p), v in confusion_counts.items() if a == b and p != b)
        prec = round(tp / (tp + fp) * 100.0, 2) if (tp + fp) > 0 else 0.0
        rec = round(tp / (tp + fn) * 100.0, 2) if (tp + fn) > 0 else 0.0
        f1 = round(2.0 * prec * rec / (prec + rec), 2) if (prec + rec) > 0 else 0.0
        metrics_per_band[b] = {
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "support": sum(v for (a, _), v in confusion_counts.items() if a == b)
        }

    macro_f1 = round(sum(m["f1_score"] for m in metrics_per_band.values()) / len(bands), 2)

    # 5. Salary Band Averages & Market Stats (aggregateByKey & mean action)
    band_averages = jobs_rdd.map(
        lambda j: (j["band"], j["salary_lpa"])
    ).aggregateByKey((0.0, 0), *add_tuple).mapValues(lambda v: round(v[0] / v[1], 2)).collectAsMap()

    overall_avg_lpa = round(jobs_rdd.map(lambda j: j["salary_lpa"]).mean(), 2)
    highest_lpa = round(max(j["salary_lpa"] for j in jobs_rdd.take(500)), 2) if total_postings else 0.0
    highest_lpa = round(jobs_rdd.map(lambda j: j["salary_lpa"]).sortBy(lambda x: x, ascending=False).first(), 2)

    # 6. Skill Market & Stock Intelligence (flatMap, reduceByKey, slope)
    month_totals = jobs_rdd.map(lambda j: j["month"]).countByValue()
    sorted_months = sorted(month_totals.keys())

    # Skill salary totals
    skill_salary_totals = jobs_rdd.flatMap(
        lambda j: [(s, j["salary_lpa"]) for s in j["skills"]]
    ).aggregateByKey((0.0, 0), *add_tuple).collectAsMap()

    # Skill monthly series: ((skill, month), count) -> (skill, [(month, count)])
    skill_monthly_counts = jobs_rdd.flatMap(
        lambda j: [((s, j["month"]), 1) for s in j["skills"]]
    ).reduceByKey(add).map(
        lambda kv: (kv[0][0], [(kv[0][1], kv[1])])
    ).reduceByKey(add).collectAsMap()

    skill_market = []
    max_skill_count = 0
    raw_skill_stats = {}

    for s in SKILLS_CANONICAL:
        m_counts = dict(skill_monthly_counts.get(s, []))
        total_s_count = sum(m_counts.values())
        max_skill_count = max(max_skill_count, total_s_count)
        shares = [
            round((m_counts.get(m, 0) / (month_totals.get(m, 1) or 1)) * 100.0, 2)
            for m in sorted_months
        ]
        mom = slope_percentage(shares)
        vol = variance(shares)
        sal_tot, sal_n = skill_salary_totals.get(s, (0.0, 0))
        skill_avg_lpa = round(sal_tot / sal_n, 2) if sal_n else 0.0
        premium = round(skill_avg_lpa - overall_avg_lpa, 2) if sal_n else 0.0

        # Financial Status Label
        if mom > 1.2:
            status = "Rising"
        elif mom < -1.2:
            status = "Falling"
        else:
            status = "Stable"

        raw_skill_stats[s] = {
            "name": s,
            "count": total_s_count,
            "demand_percent": round(total_s_count / total_postings * 100.0, 2),
            "series": shares,
            "momentum": mom,
            "volatility": vol,
            "status": status,
            "avg_lpa": skill_avg_lpa,
            "premium": premium
        }

    # Normalize Demand Index 0-100 (Stock Market index style)
    for s, data in raw_skill_stats.items():
        demand_index = round((data["count"] / max(1, max_skill_count)) * 100.0, 1)
        data["demand_index"] = demand_index
        skill_market.append(data)

    skill_market.sort(key=lambda x: -x["demand_index"])

    # 7. Role Intelligence (aggregateByKey & top skills)
    role_salary_stats = jobs_rdd.map(
        lambda j: (j["title"], j["salary_lpa"])
    ).aggregateByKey((0.0, 0), *add_tuple).collectAsMap()

    role_skill_pairs = jobs_rdd.flatMap(
        lambda j: [((j["title"], s), 1) for s in j["skills"]]
    ).reduceByKey(add).collect()

    role_intelligence = []
    for title, (tot_sal, count) in role_salary_stats.items():
        role_skills = sorted(
            ((s, round(c / count * 100.0, 1)) for (r, s), c in role_skill_pairs if r == title),
            key=lambda x: -x[1]
        )[:8]
        role_intelligence.append({
            "title": title,
            "postings_count": count,
            "avg_salary_lpa": round(tot_sal / count, 2),
            "top_skills": [[s, pct] for s, pct in role_skills]
        })
    role_intelligence.sort(key=lambda x: -x["avg_salary_lpa"])

    # 8. Company Intelligence (aggregateByKey, groupByKey, work modes)
    company_stats = jobs_rdd.map(
        lambda j: (j["company"], j["salary_lpa"])
    ).aggregateByKey((0.0, 0), *add_tuple).collectAsMap()

    company_work_modes = jobs_rdd.map(
        lambda j: ((j["company"], j["work_mode"]), 1)
    ).reduceByKey(add).collect()

    company_top_skills = jobs_rdd.flatMap(
        lambda j: [((j["company"], s), 1) for s in j["skills"]]
    ).reduceByKey(add).collect()

    company_intelligence = []
    for comp, (tot_sal, count) in company_stats.items():
        modes = {m: c for (c_name, m), c in company_work_modes if c_name == comp}
        comp_skills = sorted(
            [s for (c_name, s), c in company_top_skills if c_name == comp],
            key=lambda s: -sum(c for (c_name, sk), c in company_top_skills if c_name == comp and sk == s)
        )[:5]
        company_intelligence.append({
            "company": comp,
            "postings_count": count,
            "avg_salary_lpa": round(tot_sal / count, 2),
            "work_modes": {
                "hybrid": round(modes.get("Hybrid", 0) / count * 100.0, 1),
                "remote": round(modes.get("Remote", 0) / count * 100.0, 1),
                "onsite": round(modes.get("Onsite", 0) / count * 100.0, 1)
            },
            "top_skills": comp_skills
        })
    company_intelligence.sort(key=lambda x: -x["postings_count"])

    # 9. City / Location Intelligence (aggregateByKey & distinct)
    city_stats = jobs_rdd.map(
        lambda j: (j["city"], j["salary_lpa"])
    ).aggregateByKey((0.0, 0), *add_tuple).collectAsMap()

    city_intelligence = sorted([
        {
            "city": c,
            "postings_count": n,
            "avg_salary_lpa": round(tot / n, 2)
        }
        for c, (tot, n) in city_stats.items()
    ], key=lambda x: -x["avg_salary_lpa"])

    # 10. Distinct Categories & Distributions (distinct, countByValue)
    categories = jobs_rdd.map(lambda j: j["category"]).distinct().collect()
    work_mode_dist = jobs_rdd.map(lambda j: j["work_mode"]).countByValue()
    experience_dist = jobs_rdd.map(lambda j: j["experience"]).countByValue()
    emp_type_dist = jobs_rdd.map(lambda j: j["employment_type"]).countByValue()

    # 11. Co-occurring Skill Pairs Mining (combinations, reduceByKey, takeOrdered)
    skill_pairs = jobs_rdd.flatMap(
        lambda j: [(p, 1) for p in combinations(j["skills"], 2)]
    ).reduceByKey(add).takeOrdered(20, key=lambda kv: -kv[1])

    formatted_pairs = [
        {"skill_a": pair[0], "skill_b": pair[1], "frequency": count}
        for (pair, count) in skill_pairs
    ]

    # 12. Model Evaluation Metadata & Full Output Structure
    execution_seconds = round(time.time() - start_time, 2)

    output_payload = {
        "metadata": {
            "total_postings": total_postings,
            "total_skills": len(SKILLS_CANONICAL),
            "total_companies": len(company_stats),
            "total_cities": len(city_stats),
            "overall_avg_lpa": overall_avg_lpa,
            "highest_lpa": highest_lpa,
            "model_accuracy": overall_accuracy,
            "macro_f1_score": macro_f1,
            "engine": active_engine,
            "partitions": jobs_rdd.getNumPartitions(),
            "execution_seconds": execution_seconds,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "evaluation": {
            "accuracy": overall_accuracy,
            "macro_f1": macro_f1,
            "per_band_metrics": metrics_per_band,
            "confusion_matrix": [
                {"actual": a, "pred": p, "count": count}
                for (a, p), count in confusion_counts.items()
            ],
            "bands": bands,
            "class_distribution": class_counts,
            "band_averages": band_averages,
            "naive_bayes_model": {
                "class_counts": class_counts,
                "feature_counts": {f"{c}_{f}": v for (c, f), v in feature_counts.items()}
            }
        },
        "distributions": {
            "work_mode": dict(work_mode_dist),
            "experience": dict(experience_dist),
            "employment_type": dict(emp_type_dist),
            "categories": categories
        },
        "skills": skill_market,
        "roles": role_intelligence,
        "companies": company_intelligence,
        "cities": city_intelligence,
        "skill_pairs": formatted_pairs,
        "months": sorted_months
    }

    # Persist JSON and JS for high-speed client-side and backend loading
    json_path = os.path.join(output_dir, "insights.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    js_path = os.path.join(output_dir, "insights.js")
    compact_json = json.dumps(output_payload, separators=(",", ":"))
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(f"window.INSIGHTS = {compact_json};")

    print(f"Pipeline completed successfully in {execution_seconds}s!")
    print(f"Engine: {active_engine}")
    print(f"Postings: {total_postings} | Accuracy: {overall_accuracy}% | Macro F1: {macro_f1}%")
    print(f"Artifacts saved -> {output_dir}")

    if spark:
        spark.stop()

    return output_payload


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(data_csv_path=csv_file)
