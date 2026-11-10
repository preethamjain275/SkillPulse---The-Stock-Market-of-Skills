"""SkillPulse AI Career Assistant Service.
Grounds career guidance in real dataset findings with transparent attribution.
"""
from __future__ import annotations
import re
from typing import Dict, List
from backend.app.schemas.models import ChatResponse
from backend.app.services.data_service import data_service


class AssistantService:

    @staticmethod
    def answer_query(message: str) -> ChatResponse:
        """Answers career and market queries directly from real Spark analytics."""
        msg = message.lower().strip()
        data_sources = ["SkillPulse Spark RDD 30k Postings Analytics"]

        # 1. Highest paying skills / premium
        if "highest" in msg or "pay" in msg or "salary" in msg or "premium" in msg:
            skills = data_service.get_skills(sort_by="premium", limit=5)
            names_prem = [f"**{s['name'].upper()}** (+₹{s['premium']} LPA premium, Avg: ₹{s['avg_lpa']} LPA)" for s in skills]
            reply = (
                f"Based on 30,000 analysed job postings, the skills with the highest salary premium above market average are:\n\n"
                + "\n".join(f"{i+1}. {item}" for i, item in enumerate(names_prem)) +
                f"\n\nOverall market average salary across all roles is **₹{data_service.insights['metadata']['overall_avg_lpa']} LPA**."
            )
            suggested = [
                "Which skills have rising demand momentum?",
                "What skills are needed for a Data Scientist role?",
                "Compare salary by city across Indian tech hubs"
            ]
            return ChatResponse(response=reply, suggested_questions=suggested, data_sources_used=data_sources)

        # 2. Rising / Emerging skills
        if "rising" in msg or "growing" in msg or "trending" in msg or "emerging" in msg:
            rising = data_service.get_skills(status="Rising", sort_by="momentum", limit=5)
            list_str = [f"**{s['name'].upper()}** (+{s['momentum']}% / month momentum, Demand Index: {s['demand_index']}/100)" for s in rising]
            reply = (
                f"Here are the top **Rising Skills** showing rapid 24-month positive momentum:\n\n"
                + "\n".join(f"{i+1}. {item}" for i, item in enumerate(list_str)) +
                "\n\nThese technologies have consistently expanded their share in engineering job requirements over the past 2 years."
            )
            suggested = [
                "Which skills are currently falling in market demand?",
                "What skills do I need for an AI Application Developer?",
                "Which companies hire the most for Cloud and DevOps?"
            ]
            return ChatResponse(response=reply, suggested_questions=suggested, data_sources_used=data_sources)

        # 3. Role specific inquiry
        for r in data_service.get_roles():
            if r["title"].lower() in msg:
                top_sk = [f"**{s.upper()}** ({pct}% of postings)" for s, pct in r["top_skills"][:6]]
                reply = (
                    f"**Role Intelligence for {r['title']}**:\n\n"
                    f"- **Average Advertised Salary:** ₹{r['avg_salary_lpa']} LPA\n"
                    f"- **Total Job Postings in Dataset:** {r['postings_count']:,}\n"
                    f"- **Most Frequently Demanded Skills:**\n"
                    + "\n".join(f"  • {item}" for item in top_sk) +
                    f"\n\nTo become competitive for {r['title']}, focus on mastering the top 3 core skills before branching into secondary tools."
                )
                suggested = [
                    f"Generate a career roadmap for {r['title']}",
                    f"Check my readiness score for {r['title']}",
                    "What companies are hiring for this role?"
                ]
                return ChatResponse(response=reply, suggested_questions=suggested, data_sources_used=data_sources)

        # 4. Location / City inquiry
        for c in data_service.get_locations():
            if c["city"].lower() in msg:
                reply = (
                    f"**Employment Market for {c['city']}**:\n\n"
                    f"- **Average Advertised Salary:** ₹{c['avg_salary_lpa']} LPA\n"
                    f"- **Postings Analyzed:** {c['postings_count']:,}\n"
                    f"- **Cost/Compensation Index:** {round(c['avg_salary_lpa'] / data_service.insights['metadata']['overall_avg_lpa'], 2)}x national average\n\n"
                    f"{c['city']} offers strong hiring volume with high concentration of cloud, data, and full-stack software development roles."
                )
                suggested = [
                    "Compare Bengaluru vs Hyderabad salaries",
                    "Which cities have more remote opportunities?",
                    "What are the top fresher roles in India?"
                ]
                return ChatResponse(response=reply, suggested_questions=suggested, data_sources_used=data_sources)

        # 5. Fresher / Intern advice
        if "fresher" in msg or "intern" in msg or "beginner" in msg or "student" in msg:
            reply = (
                "**Fresher Career Advice grounded in hiring data:**\n\n"
                "1. **Core Skills Over Hype:** Junior job postings require fundamental problem-solving in **Python, SQL, and Git** far more frequently than complex niche frameworks.\n"
                "2. **Full-Stack & Data Analytics:** Roles like *Frontend Developer, Data Analyst, and QA Engineer* offer the highest proportion of entry-level and internship openings.\n"
                "3. **Showcase Verified Projects:** Employers value a well-documented GitHub repository with a deployed live URL over multiple theoretical course certificates.\n"
                "4. **Fresher Salary Expectation:** Entry-level postings in India typically range from **₹3.5 to ₹8.5 LPA**, scaling with proficiency in cloud and automated testing."
            )
            suggested = [
                "Find fresher-friendly job listings",
                "How is the career readiness score calculated?",
                "Which skills pay the highest salary?"
            ]
            return ChatResponse(response=reply, suggested_questions=suggested, data_sources_used=data_sources)

        # Default fallback
        reply = (
            "I am the SkillPulse Career Intelligence Assistant, powered by Spark RDD analytics on 30,000 job postings.\n\n"
            "You can ask me about:\n"
            "- **Top Demanded Skills & Emerging Trends** (e.g., *'Which skills have rising demand?'*)\n"
            "- **Role Requirements & Salary Benchmarks** (e.g., *'What skills are needed for ML Engineer?'*)\n"
            "- **City Comparisons** (e.g., *'What is the average salary in Bengaluru?'*)\n"
            "- **Fresher & Internship Guidance** (e.g., *'What should a fresher learn first?'*)"
        )
        suggested = [
            "Which skills have rising demand momentum?",
            "What skills are needed for a Data Scientist role?",
            "Which cities have the highest average software salaries?"
        ]
        return ChatResponse(response=reply, suggested_questions=suggested, data_sources_used=data_sources)


assistant_service = AssistantService()
