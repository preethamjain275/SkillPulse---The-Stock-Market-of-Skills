"""SkillPulse Machine Learning & Inference Service.
Evaluates Naive Bayes classification, statistical salary prediction,
skill gap identification, career roadmaps, and student readiness.
"""
from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.models import (
    PredictResponse,
    SalaryPredictResponse,
    SkillGapResponse,
    MissingSkillDetail,
    RoadmapResponse,
    RoadmapStage,
    ReadinessResponse
)
from backend.app.services.data_service import data_service

CITY_COST_INDEX = {
    "Bengaluru": 1.20,
    "Mumbai": 1.15,
    "Delhi NCR": 1.10,
    "Hyderabad": 1.08,
    "Pune": 1.02,
    "Chennai": 0.98,
    "Kolkata": 0.88,
    "Mysuru": 0.82,
    "Kochi": 0.80
}

EXP_MULTIPLIER = {
    "intern": 0.35,
    "junior": 0.80,
    "mid": 1.25,
    "senior": 1.85
}

ROLE_BASE_SALARY = {
    "ML Engineer": 16.5,
    "AI Application Developer": 15.0,
    "Data Engineer": 14.0,
    "Cloud Engineer": 13.5,
    "Data Scientist": 13.5,
    "DevOps Engineer": 13.0,
    "Cybersecurity Analyst": 12.0,
    "Full Stack Developer": 11.5,
    "Backend Developer": 11.0,
    "Frontend Developer": 8.5,
    "Android Developer": 8.5,
    "Data Analyst": 7.5,
    "QA Engineer": 6.5
}

SKILL_PREMIUM_DEFAULTS = {
    "genai": 4.5, "langchain": 3.5, "rust": 4.0, "kubernetes": 3.0, "spark": 3.0,
    "pytorch": 2.5, "aws": 2.0, "azure": 1.5, "typescript": 1.2, "docker": 1.2,
    "python": 1.0, "react": 0.8, "sql": 0.5, "node": 0.8, "java": 0.6,
    "excel": -0.8, "jquery": -1.0, "selenium": -0.5, "angular": -0.4, "hadoop": -0.5
}


class MLService:

    @staticmethod
    def classify_salary_band(
        skills: List[str],
        experience: str = "junior",
        category: Optional[str] = None,
        work_mode: Optional[str] = None
    ) -> PredictResponse:
        """Evaluates Spark-trained Naive Bayes model parameters."""
        eval_data = data_service.get_model_evaluation()
        nb_model = eval_data.get("naive_bayes_model", {})
        class_counts = nb_model.get("class_counts", {"Low": 1000, "Mid": 1500, "High": 1000})
        feat_counts = nb_model.get("feature_counts", {})
        bands = eval_data.get("bands", ["Low", "Mid", "High"])

        total_docs = sum(class_counts.values()) or 1

        features = [f"sk_{s.lower()}" for s in skills]
        features.append(f"lvl_{experience.lower()}")
        if category:
            features.append(f"cat_{category}")
        if work_mode:
            features.append(f"mode_{work_mode}")

        log_probs = {}
        for b in bands:
            c_cnt = class_counts.get(b, 1)
            lp = math.log((c_cnt + 1.0) / (total_docs + len(bands)))
            for f in features:
                cnt = feat_counts.get(f"{b}_{f}", 0)
                lp += math.log((cnt + 1.0) / (c_cnt + 2.0))
            log_probs[b] = lp

        max_lp = max(log_probs.values())
        exp_vals = {b: math.exp(lp - max_lp) for b, lp in log_probs.items()}
        sum_exp = sum(exp_vals.values()) or 1.0
        probabilities = {b: round(exp_vals[b] / sum_exp * 100.0, 1) for b in bands}

        predicted_band = max(probabilities, key=probabilities.get)
        confidence = probabilities[predicted_band]

        return PredictResponse(
            predicted_band=predicted_band,
            band_probabilities=probabilities,
            confidence=confidence,
            features_used=features,
            disclaimer="Predicted using Naive Bayes classifier trained on 30,000 job postings via Apache Spark RDD transformations with Laplace smoothing."
        )

    @staticmethod
    def predict_salary_range(
        role: str,
        skills: List[str],
        experience: str = "junior",
        city: str = "Bengaluru"
    ) -> SalaryPredictResponse:
        """Statistical salary range estimation with city and skill weighting."""
        base_lpa = ROLE_BASE_SALARY.get(role, 10.0)
        exp_mult = EXP_MULTIPLIER.get(experience.lower(), 0.8)
        city_mult = CITY_COST_INDEX.get(city, 1.0)

        # Retrieve actual skill premiums from Spark analytics if available
        bonuses = {}
        total_bonus = 0.0
        for s in skills:
            s_clean = s.lower()
            s_meta = data_service.get_skill_detail(s_clean)
            if s_meta and "premium" in s_meta:
                prem = max(-1.0, min(5.0, s_meta["premium"] * 0.4))
            else:
                prem = SKILL_PREMIUM_DEFAULTS.get(s_clean, 0.0)
            bonuses[s] = round(prem, 2)
            total_bonus += prem

        raw_estimated = (base_lpa + total_bonus) * exp_mult * city_mult
        raw_estimated = max(2.8, raw_estimated)

        median_lpa = round(raw_estimated, 1)
        min_lpa = round(max(2.5, raw_estimated * 0.85), 1)
        max_lpa = round(raw_estimated * 1.20, 1)

        band = "Low" if median_lpa < 8.0 else "Mid" if median_lpa < 18.0 else "High"

        return SalaryPredictResponse(
            estimated_lpa_min=min_lpa,
            estimated_lpa_median=median_lpa,
            estimated_lpa_max=max_lpa,
            predicted_band=band,
            city_factor=city_mult,
            experience_multiplier=exp_mult,
            skill_bonuses=bonuses,
            disclaimer="Salary estimates are statistical predictions based on available job-market data. Actual compensation varies by employer, experience, location and other factors."
        )

    @staticmethod
    def analyze_skill_gap(
        current_skills: List[str],
        target_role: str,
        experience: str = "junior",
        location: str = "Bengaluru"
    ) -> SkillGapResponse:
        """Identifies missing skills, role frequency weights, and optimal learning sequence."""
        current_set = {s.lower() for s in current_skills}
        role_data = data_service.roles_by_title.get(target_role.lower())

        if not role_data:
            # Fallback to closest role
            role_data = data_service.get_roles()[0]

        top_role_skills = role_data.get("top_skills", [])
        total_weight = sum(pct for _, pct in top_role_skills) or 1.0
        possessed_weight = sum(pct for s, pct in top_role_skills if s.lower() in current_set)

        match_pct = round((possessed_weight / total_weight) * 100.0, 1)

        possessed = [s for s, _ in top_role_skills if s.lower() in current_set]
        missing_list: List[MissingSkillDetail] = []

        for s, freq in top_role_skills:
            if s.lower() not in current_set:
                s_meta = data_service.get_skill_detail(s)
                premium = s_meta.get("premium", 0.0) if s_meta else 0.0
                status = s_meta.get("status", "Stable") if s_meta else "Stable"

                if freq >= 70.0:
                    priority = "Critical"
                elif freq >= 40.0:
                    priority = "High"
                elif freq >= 25.0:
                    priority = "Medium"
                else:
                    priority = "Nice-to-have"

                missing_list.append(MissingSkillDetail(
                    skill=s,
                    frequency_in_role_pct=freq,
                    salary_premium_lpa=premium,
                    market_status=status,
                    priority=priority
                ))

        # Sort missing skills by frequency descending
        missing_list.sort(key=lambda x: -x.frequency_in_role_pct)

        learning_order = [m.skill for m in missing_list]

        # Find related roles with overlapping skill requirements
        related_roles = []
        for r in data_service.get_roles():
            if r["title"].lower() != role_data["title"].lower():
                r_skills = {sk for sk, _ in r.get("top_skills", [])}
                overlap = len(current_set & r_skills)
                if overlap > 0:
                    related_roles.append({
                        "role": r["title"],
                        "overlap_skills_count": overlap,
                        "avg_lpa": r["avg_salary_lpa"]
                    })
        related_roles.sort(key=lambda x: -x["overlap_skills_count"])

        return SkillGapResponse(
            target_role=role_data["title"],
            role_avg_lpa=role_data["avg_salary_lpa"],
            role_postings_count=role_data["postings_count"],
            match_percentage=match_pct,
            possessed_skills=possessed,
            missing_skills=missing_list,
            recommended_learning_order=learning_order,
            related_roles=related_roles[:4]
        )

    @staticmethod
    def generate_career_roadmap(
        target_role: str,
        current_skills: Optional[List[str]] = None
    ) -> RoadmapResponse:
        """Generates realistic curriculum roadmap tailored to job requirements."""
        gap = MLService.analyze_skill_gap(current_skills or [], target_role)
        missing = [m.skill for m in gap.missing_skills]

        # Pre-curated stages customized by target role
        stage_templates = {
            "Data Scientist": [
                RoadmapStage(
                    stage_number=1,
                    title="Mathematical Foundations & Advanced SQL",
                    skills_to_learn=["sql", "excel"],
                    why_it_matters="Real-world data science begins with querying production relational databases and verifying data cleanliness.",
                    estimated_duration_weeks=3,
                    recommended_project="E-commerce Retention & Churn Cohort SQL Queries",
                    practical_exercises=["Write multi-table window functions (LEAD/LAG, RANK)", "Design a 3NF normalized schema for job postings"],
                    expected_outcome="Able to extract, aggregate, and inspect complex analytical datasets independently."
                ),
                RoadmapStage(
                    stage_number=2,
                    title="Python Data Manipulation & Exploratory Analysis",
                    skills_to_learn=["python", "pandas"],
                    why_it_matters="Pandas is the de-facto standard for vectorized transformations, anomaly detection, and data wrangling.",
                    estimated_duration_weeks=4,
                    recommended_project="Automated Exploratory Data Analysis (EDA) Pipeline on 100k Records",
                    practical_exercises=["Implement custom aggregation and pivot table pipelines", "Handle missing values via statistical imputation"],
                    expected_outcome="Capable of cleaning messy datasets and generating publication-ready statistical profiles."
                ),
                RoadmapStage(
                    stage_number=3,
                    title="Statistical Machine Learning & Model Evaluation",
                    skills_to_learn=["sklearn"],
                    why_it_matters="Employers look for rigorous validation: confusion matrices, precision/recall trade-offs, and feature selection.",
                    estimated_duration_weeks=4,
                    recommended_project="Salary Band Classifier with Hyperparameter Grid Search & Cross Validation",
                    practical_exercises=["Implement Naive Bayes from scratch using count ratios", "Compare Random Forests with Gradient Boosting"],
                    expected_outcome="Deep understanding of ML evaluation metrics, avoiding data leakage, and packaging models."
                ),
                RoadmapStage(
                    stage_number=4,
                    title="Deep Learning, Large Scale Distributed Compute & GenAI",
                    skills_to_learn=["pytorch", "spark", "genai", "langchain"],
                    why_it_matters="Modern AI roles demand knowledge of LLM orchestration (RAG) and distributed big data pipelines.",
                    estimated_duration_weeks=5,
                    recommended_project="Enterprise Document Retrieval & Question-Answering Assistant (RAG Pipeline)",
                    practical_exercises=["Build an RDD aggregation pipeline processing 1M rows", "Construct LangChain semantic search with vector embeddings"],
                    expected_outcome="Portfolio project demonstrating end-to-end GenAI application development."
                )
            ]
        }

        # Fallback dynamic stages if role not in template
        stages = stage_templates.get(target_role)
        if not stages:
            chunk_size = max(1, math.ceil(len(missing) / 4)) if missing else 1
            chunks = [missing[i:i + chunk_size] for i in range(0, len(missing), chunk_size)]
            stages = []
            for idx, ch in enumerate(chunks[:4]):
                stages.append(RoadmapStage(
                    stage_number=idx + 1,
                    title=f"Phase {idx + 1}: Mastering {', '.join(s.upper() for s in ch)}",
                    skills_to_learn=ch,
                    why_it_matters=f"Directly addresses {len(ch)} high-demand skills required for {target_role}.",
                    estimated_duration_weeks=3 + idx,
                    recommended_project=f"Production-ready {target_role} Capstone integrating {', '.join(ch)}",
                    practical_exercises=[f"Complete 5 hands-on projects practicing {s}" for s in ch],
                    expected_outcome=f"Industry-ready proficiency in {', '.join(ch)}."
                ))

        total_weeks = sum(s.estimated_duration_weeks for s in stages)

        free_resources = [
            {"title": "CS50 Introduction to Computer Science (Harvard)", "url": "https://cs50.harvard.edu/"},
            {"title": "freeCodeCamp Full-Stack Certification", "url": "https://www.freecodecamp.org/"},
            {"title": "Apache Spark Official RDD Programming Guide", "url": "https://spark.apache.org/docs/latest/rdd-programming-guide.html"},
            {"title": "FastAPI Official Interactive Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"},
            {"title": "Kaggle Learn Free Practical Micro-Courses", "url": "https://www.kaggle.com/learn"}
        ]

        fresher_tips = [
            "Build 2-3 deep, deployed GitHub projects rather than 20 trivial tutorials.",
            "Always include a clean README with architecture diagram and live demonstration link.",
            "Write tests and documentation for your code to stand out from 90% of applicants.",
            "Contribute to open-source or reproduce a research paper's findings."
        ]

        return RoadmapResponse(
            target_role=target_role,
            total_estimated_weeks=total_weeks,
            stages=stages,
            fresher_tips=fresher_tips,
            free_resources=free_resources
        )

    @staticmethod
    def evaluate_readiness(
        skills: List[str],
        target_role: str,
        experience: str = "junior",
        has_projects: bool = True
    ) -> ReadinessResponse:
        """Calculates transparent readiness score out of 100 with clear formula breakdown."""
        gap = MLService.analyze_skill_gap(skills, target_role, experience)
        skill_coverage = gap.match_percentage

        # Transparent Formula:
        # 1. Skill Coverage (up to 60 points)
        skill_points = round((skill_coverage / 100.0) * 60.0)

        # 2. Critical Skill Completeness (up to 20 points)
        critical_missing = [m for m in gap.missing_skills if m.priority == "Critical"]
        if not critical_missing:
            critical_points = 20
        else:
            critical_points = max(0, 20 - (len(critical_missing) * 7))

        # 3. Portfolio Projects (up to 15 points)
        project_points = 15 if has_projects else 5

        # 4. Git / Core Engineering Hygiene (up to 5 points)
        has_git = "git" in [s.lower() for s in skills]
        hygiene_points = 5 if has_git else 0

        total_score = min(100, max(0, skill_points + critical_points + project_points + hygiene_points))

        if total_score >= 80:
            readiness_level = "Job Ready"
        elif total_score >= 60:
            readiness_level = "Near Ready"
        elif total_score >= 40:
            readiness_level = "Developing"
        else:
            readiness_level = "Early Explorer"

        recommended_projects = [
            f"End-to-End {target_role} Showcase Application with live deployment and CI/CD",
            "Open Source Contribution to a recognized ecosystem repository",
            "Comprehensive benchmark study comparing 2 architectural approaches"
        ]

        next_steps = [
            f"Close critical gaps in: {', '.join(m.skill for m in critical_missing[:2]) or 'Advanced Domain Knowledge'}",
            "Deploy your portfolio projects on cloud hosting (Vercel/Render/AWS Free Tier)",
            "Practice technical interview fundamentals on Data Structures & System Design"
        ]

        formula_text = (
            f"Score = Skill Coverage ({skill_points}/60) + Critical Skills ({critical_points}/20) + "
            f"Projects ({project_points}/15) + Engineering Hygiene ({hygiene_points}/5) = {total_score}/100"
        )

        return ReadinessResponse(
            readiness_score=total_score,
            readiness_level=readiness_level,
            skill_coverage_pct=skill_coverage,
            scoring_breakdown={
                "skill_coverage_points": skill_points,
                "critical_skills_points": critical_points,
                "project_portfolio_points": project_points,
                "hygiene_points": hygiene_points
            },
            strengths=gap.possessed_skills,
            critical_gaps=[m.skill for m in critical_missing],
            recommended_projects=recommended_projects,
            next_steps=next_steps,
            transparent_formula=formula_text
        )


ml_service = MLService()
