"""SkillPulse Data Service.
Manages in-memory cache of Spark RDD analytics insights and CSV queries.
"""
from __future__ import annotations
import csv
import json
import os
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings
from backend.spark.pipeline import run_pipeline


class DataService:
    _instance: Optional[DataService] = None

    def __init__(self):
        self.insights: Dict[str, Any] = {}
        self.raw_jobs: List[Dict[str, Any]] = []
        self.skills_by_name: Dict[str, Dict[str, Any]] = {}
        self.roles_by_title: Dict[str, Dict[str, Any]] = {}
        self.companies_by_name: Dict[str, Dict[str, Any]] = {}
        self.cities_by_name: Dict[str, Dict[str, Any]] = {}
        self.load_data()

    @classmethod
    def get_instance(cls) -> DataService:
        if cls._instance is None:
            cls._instance = DataService()
        return cls._instance

    def load_data(self) -> None:
        """Loads or computes analytical insights and loads job records."""
        # 1. Ensure insights exist
        if not os.path.exists(settings.INSIGHTS_JSON_PATH):
            print("Insights not found on disk, running Spark RDD pipeline...")
            self.insights = run_pipeline()
        else:
            with open(settings.INSIGHTS_JSON_PATH, "r", encoding="utf-8") as f:
                self.insights = json.load(f)

        # 2. Build index dictionaries for O(1) lookups
        for s in self.insights.get("skills", []):
            self.skills_by_name[s["name"].lower()] = s

        for r in self.insights.get("roles", []):
            self.roles_by_title[r["title"].lower()] = r

        for c in self.insights.get("companies", []):
            self.companies_by_name[c["company"].lower()] = c

        for ci in self.insights.get("cities", []):
            self.cities_by_name[ci["city"].lower()] = ci

        # 3. Load sample of CSV postings for explorer
        if os.path.exists(settings.DATA_CSV_PATH):
            with open(settings.DATA_CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.raw_jobs = list(reader)

    def get_overview(self) -> Dict[str, Any]:
        """Returns top-level KPIs and distributions for the dashboard."""
        return {
            "metadata": self.insights.get("metadata", {}),
            "distributions": self.insights.get("distributions", {}),
            "top_skills": self.insights.get("skills", [])[:8],
            "top_roles": self.insights.get("roles", [])[:6],
            "top_cities": self.insights.get("cities", [])[:6],
            "skill_pairs": self.insights.get("skill_pairs", [])[:8]
        }

    def get_skills(
        self,
        status: Optional[str] = None,
        sort_by: str = "demand_index",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Returns skill market data with optional filtering and sorting."""
        skills = list(self.insights.get("skills", []))
        if status and status.lower() != "all":
            skills = [s for s in skills if s.get("status", "").lower() == status.lower()]

        reverse = True
        if sort_by == "name":
            reverse = False

        skills.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
        return skills[:limit]

    def get_skill_detail(self, skill_name: str) -> Optional[Dict[str, Any]]:
        return self.skills_by_name.get(skill_name.lower())

    def get_roles(self) -> List[Dict[str, Any]]:
        return self.insights.get("roles", [])

    def get_companies(self) -> List[Dict[str, Any]]:
        return self.insights.get("companies", [])

    def get_company_detail(self, company_name: str) -> Optional[Dict[str, Any]]:
        return self.companies_by_name.get(company_name.lower())

    def get_locations(self) -> List[Dict[str, Any]]:
        return self.insights.get("cities", [])

    def get_model_evaluation(self) -> Dict[str, Any]:
        return self.insights.get("evaluation", {})

    def query_jobs(
        self,
        city: Optional[str] = None,
        role: Optional[str] = None,
        company: Optional[str] = None,
        experience: Optional[str] = None,
        work_mode: Optional[str] = None,
        skill: Optional[str] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Filters raw job postings with pagination."""
        filtered = self.raw_jobs

        if city and city.lower() != "all":
            filtered = [j for j in filtered if j.get("city", "").lower() == city.lower()]
        if role and role.lower() != "all":
            filtered = [j for j in filtered if role.lower() in j.get("title", "").lower()]
        if company and company.lower() != "all":
            filtered = [j for j in filtered if j.get("company", "").lower() == company.lower()]
        if experience and experience.lower() != "all":
            filtered = [j for j in filtered if j.get("experience", "").lower() == experience.lower()]
        if work_mode and work_mode.lower() != "all":
            filtered = [j for j in filtered if j.get("work_mode", "").lower() == work_mode.lower()]
        if skill and skill.lower() != "all":
            filtered = [j for j in filtered if skill.lower() in j.get("description", "").lower()]
        if min_salary is not None:
            filtered = [j for j in filtered if float(j.get("salary_lpa", 0)) >= min_salary]
        if max_salary is not None:
            filtered = [j for j in filtered if float(j.get("salary_lpa", 0)) <= max_salary]

        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        items = filtered[start:end]

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size else 1,
            "items": items
        }

    def get_fresher_jobs(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Returns fresher and internship postings."""
        freshers = [
            j for j in self.raw_jobs
            if j.get("experience", "").lower() in ("intern", "junior")
        ]
        total = len(freshers)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "items": freshers[start:end]
        }


data_service = DataService.get_instance()
