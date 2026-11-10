"""Comprehensive Unit & Integration Test Suite for SkillPulse Backend & ML Services."""
import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.services.data_service import data_service
from backend.app.services.ml_service import ml_service
from backend.app.services.assistant_service import assistant_service
from backend.app.schemas.models import (
    PredictRequest,
    SalaryPredictRequest,
    SkillGapRequest,
    RoadmapRequest,
    ReadinessRequest,
    ChatRequest
)


def test_data_service_initialization():
    assert len(data_service.raw_jobs) == 30000
    overview = data_service.get_overview()
    assert "metadata" in overview
    assert "top_skills" in overview
    assert len(overview["top_skills"]) == 8


def test_skills_filtering():
    rising = data_service.get_skills(status="Rising", limit=10)
    assert len(rising) > 0
    for s in rising:
        assert s["status"] == "Rising"

    top = data_service.get_skills(sort_by="demand_index", limit=5)
    assert len(top) == 5
    assert top[0]["demand_index"] >= top[-1]["demand_index"]


def test_naive_bayes_classification():
    skills = ["python", "pytorch", "genai", "langchain"]
    res = ml_service.classify_salary_band(skills, experience="senior", category="Artificial Intelligence")
    assert res.predicted_band in ["Low", "Mid", "High"]
    assert "Low" in res.band_probabilities
    assert "Mid" in res.band_probabilities
    assert "High" in res.band_probabilities
    total_prob = sum(res.band_probabilities.values())
    assert 99.0 <= total_prob <= 101.0


def test_salary_prediction_range():
    res = ml_service.predict_salary_range(
        role="ML Engineer",
        skills=["python", "pytorch", "aws"],
        experience="mid",
        city="Bengaluru"
    )
    assert res.estimated_lpa_min > 0
    assert res.estimated_lpa_median >= res.estimated_lpa_min
    assert res.estimated_lpa_max >= res.estimated_lpa_median
    assert res.city_factor == 1.20
    assert "statistical predictions" in res.disclaimer.lower()


def test_skill_gap_analysis():
    res = ml_service.analyze_skill_gap(
        current_skills=["python", "sql"],
        target_role="Data Scientist",
        experience="junior",
        location="Bengaluru"
    )
    assert res.target_role == "Data Scientist"
    assert 0.0 <= res.match_percentage <= 100.0
    assert len(res.missing_skills) > 0
    assert any(m.priority in ["Critical", "High", "Medium", "Nice-to-have"] for m in res.missing_skills)
    assert len(res.recommended_learning_order) > 0


def test_career_roadmap_generation():
    res = ml_service.generate_career_roadmap(
        target_role="Data Scientist",
        current_skills=["python"]
    )
    assert res.target_role == "Data Scientist"
    assert len(res.stages) >= 3
    assert res.total_estimated_weeks > 0
    assert len(res.free_resources) > 0


def test_career_readiness_scoring():
    res = ml_service.evaluate_readiness(
        skills=["python", "sql", "git"],
        target_role="Backend Developer",
        experience="junior",
        has_projects=True
    )
    assert 0 <= res.readiness_score <= 100
    assert res.readiness_level in ["Job Ready", "Near Ready", "Developing", "Early Explorer"]
    assert "Score =" in res.transparent_formula


def test_ai_career_assistant_queries():
    chat1 = assistant_service.answer_query("Which skills have rising demand?")
    assert "rising" in chat1.response.lower()
    assert len(chat1.suggested_questions) > 0

    chat2 = assistant_service.answer_query("What is the average salary in Bengaluru?")
    assert "bengaluru" in chat2.response.lower() or "salary" in chat2.response.lower()

    chat3 = assistant_service.answer_query("Fresher tips for software development")
    assert "fresher" in chat3.response.lower()


def test_jobs_query_and_filtering():
    result = data_service.query_jobs(city="Bengaluru", role="Developer", page=1, page_size=10)
    assert result["total"] > 0
    assert len(result["items"]) <= 10
    for item in result["items"]:
        assert item["city"].lower() == "bengaluru"

    freshers = data_service.get_fresher_jobs(page=1, page_size=10)
    assert freshers["total"] > 0
    for item in freshers["items"]:
        assert item["experience"].lower() in ("intern", "junior")


def test_model_evaluation_metrics():
    eval_data = data_service.get_model_evaluation()
    assert "accuracy" in eval_data
    assert "macro_f1" in eval_data
    assert "confusion_matrix" in eval_data
    assert "per_band_metrics" in eval_data
    for b in ["Low", "Mid", "High"]:
        assert b in eval_data["per_band_metrics"]
        assert "precision" in eval_data["per_band_metrics"][b]
        assert "recall" in eval_data["per_band_metrics"][b]
        assert "f1_score" in eval_data["per_band_metrics"][b]
