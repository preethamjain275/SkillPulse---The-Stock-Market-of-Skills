"""SkillPulse FastAPI API Endpoints.
Implements the complete RESTful suite for job market analytics,
classification, prediction, roadmaps, and career intelligence.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from backend.app.schemas.models import (
    PredictRequest,
    PredictResponse,
    SalaryPredictRequest,
    SalaryPredictResponse,
    SkillGapRequest,
    SkillGapResponse,
    RoadmapRequest,
    RoadmapResponse,
    ReadinessRequest,
    ReadinessResponse,
    ChatRequest,
    ChatResponse
)
from backend.app.services.data_service import data_service
from backend.app.services.ml_service import ml_service
from backend.app.services.assistant_service import assistant_service

router = APIRouter()


# 1. Health & Status
@router.get("/health", tags=["System"])
def get_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "SkillPulse Job Market Analytics API",
        "version": "2.0.0",
        "postings_loaded": len(data_service.raw_jobs),
        "spark_engine": data_service.insights.get("metadata", {}).get("engine", "Spark RDD")
    }


# 2. Dashboard Overview
@router.get("/dashboard/overview", tags=["Dashboard"])
def get_dashboard_overview() -> Dict[str, Any]:
    return data_service.get_overview()


# 3. Skills Intelligence
@router.get("/skills", tags=["Skill Market"])
def get_all_skills(
    status: Optional[str] = Query(None, description="Filter by status: All, Rising, Stable, Falling"),
    sort_by: str = Query("demand_index", description="Sort by: demand_index, momentum, premium, avg_lpa, name"),
    limit: int = Query(50, ge=1, le=100)
) -> List[Dict[str, Any]]:
    return data_service.get_skills(status=status, sort_by=sort_by, limit=limit)


@router.get("/skills/trends", tags=["Skill Market"])
def get_skill_trends() -> Dict[str, Any]:
    return {
        "months": data_service.insights.get("months", []),
        "skills": [
            {
                "name": s["name"],
                "series": s["series"],
                "status": s["status"],
                "momentum": s["momentum"],
                "demand_index": s["demand_index"]
            }
            for s in data_service.insights.get("skills", [])
        ]
    }


@router.get("/skills/top-demanded", tags=["Skill Market"])
def get_top_demanded_skills(limit: int = Query(10, ge=1, le=33)) -> List[Dict[str, Any]]:
    return data_service.get_skills(sort_by="demand_index", limit=limit)


@router.get("/skills/rising", tags=["Skill Market"])
def get_rising_skills(limit: int = Query(10, ge=1, le=33)) -> List[Dict[str, Any]]:
    return data_service.get_skills(status="Rising", sort_by="momentum", limit=limit)


@router.get("/skills/declining", tags=["Skill Market"])
def get_declining_skills(limit: int = Query(10, ge=1, le=33)) -> List[Dict[str, Any]]:
    return data_service.get_skills(status="Falling", sort_by="momentum", limit=limit)


@router.get("/skills/{skill_name}", tags=["Skill Market"])
def get_skill_detail(skill_name: str) -> Dict[str, Any]:
    detail = data_service.get_skill_detail(skill_name)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found in index.")
    return detail


# 4. Machine Learning Classification
@router.post("/classification/predict", response_model=PredictResponse, tags=["Machine Learning"])
def predict_salary_band(payload: PredictRequest) -> PredictResponse:
    if not payload.skills:
        raise HTTPException(status_code=400, detail="At least one technical skill is required.")
    return ml_service.classify_salary_band(
        skills=payload.skills,
        experience=payload.experience,
        category=payload.category,
        work_mode=payload.work_mode
    )


# 5. Salary Prediction
@router.post("/salary/predict", response_model=SalaryPredictResponse, tags=["Salary Intelligence"])
def predict_salary(payload: SalaryPredictRequest) -> SalaryPredictResponse:
    return ml_service.predict_salary_range(
        role=payload.role,
        skills=payload.skills,
        experience=payload.experience,
        city=payload.city
    )


# 6. Skill Gap Analysis
@router.post("/skill-gap/analyze", response_model=SkillGapResponse, tags=["Skill Gap"])
def analyze_skill_gap(payload: SkillGapRequest) -> SkillGapResponse:
    return ml_service.analyze_skill_gap(
        current_skills=payload.current_skills,
        target_role=payload.target_role,
        experience=payload.experience or "junior",
        location=payload.location or "Bengaluru"
    )


# 7. Career Roadmap Generator
@router.post("/career-roadmap/generate", response_model=RoadmapResponse, tags=["Career Roadmap"])
def generate_career_roadmap(payload: RoadmapRequest) -> RoadmapResponse:
    return ml_service.generate_career_roadmap(
        target_role=payload.target_role,
        current_skills=payload.current_skills
    )


# 8. Jobs Explorer
@router.get("/jobs", tags=["Jobs Explorer"])
def get_jobs(
    city: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    work_mode: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None),
    max_salary: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
) -> Dict[str, Any]:
    return data_service.query_jobs(
        city=city,
        role=role,
        company=company,
        experience=experience,
        work_mode=work_mode,
        skill=skill,
        min_salary=min_salary,
        max_salary=max_salary,
        page=page,
        page_size=page_size
    )


@router.get("/jobs/freshers", tags=["Jobs Explorer"])
def get_fresher_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
) -> Dict[str, Any]:
    return data_service.get_fresher_jobs(page=page, page_size=page_size)


# 9. Company Intelligence
@router.get("/companies", tags=["Company Intelligence"])
def get_companies() -> List[Dict[str, Any]]:
    return data_service.get_companies()


@router.get("/companies/{company_name}", tags=["Company Intelligence"])
def get_company_detail(company_name: str) -> Dict[str, Any]:
    detail = data_service.get_company_detail(company_name)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Company '{company_name}' not found.")
    return detail


# 10. Location Intelligence
@router.get("/locations", tags=["Location Intelligence"])
def get_locations() -> List[Dict[str, Any]]:
    return data_service.get_locations()


# 11. Student Career Readiness
@router.post("/career-readiness/analyze", response_model=ReadinessResponse, tags=["Readiness"])
def analyze_readiness(payload: ReadinessRequest) -> ReadinessResponse:
    return ml_service.evaluate_readiness(
        skills=payload.skills,
        target_role=payload.target_role,
        experience=payload.experience or "junior",
        has_projects=payload.has_projects if payload.has_projects is not None else True
    )


# 12. AI Career Assistant
@router.post("/career-assistant/chat", response_model=ChatResponse, tags=["Career Assistant"])
def chat_with_assistant(payload: ChatRequest) -> ChatResponse:
    return assistant_service.answer_query(payload.message)


# 13. Model Evaluation Dashboard
@router.get("/model/evaluation", tags=["Model Evaluation"])
def get_model_evaluation() -> Dict[str, Any]:
    return data_service.get_model_evaluation()


# 14. Dataset Summary
@router.get("/dataset/summary", tags=["Dataset"])
def get_dataset_summary() -> Dict[str, Any]:
    return {
        "metadata": data_service.insights.get("metadata", {}),
        "distributions": data_service.insights.get("distributions", {}),
        "dataset_columns": [
            "job_id", "title", "category", "company", "city",
            "month", "experience", "work_mode", "employment_type",
            "salary_lpa", "description"
        ]
    }
