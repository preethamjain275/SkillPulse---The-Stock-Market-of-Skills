"""SkillPulse Pydantic Schemas for API Request/Response validation."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# 1. Classification & Prediction
class PredictRequest(BaseModel):
    skills: List[str] = Field(..., description="List of technical skills possessed", example=["python", "sql", "git"])
    experience: str = Field("junior", description="Experience level: intern, junior, mid, senior", example="junior")
    category: Optional[str] = Field(None, description="Job category if known", example="Software Development")
    work_mode: Optional[str] = Field(None, description="Preferred work mode: Remote, Hybrid, Onsite")


class PredictResponse(BaseModel):
    predicted_band: str = Field(..., description="Predicted salary band: Low, Mid, or High")
    band_probabilities: Dict[str, float] = Field(..., description="Normalized posterior probabilities per band")
    confidence: float = Field(..., description="Probability of predicted class in percent")
    features_used: List[str]
    disclaimer: str


# 2. Salary Prediction
class SalaryPredictRequest(BaseModel):
    role: str = Field(..., description="Target role name", example="Data Scientist")
    skills: List[str] = Field(..., description="Selected skills", example=["python", "pandas", "sklearn"])
    experience: str = Field("junior", description="Experience level", example="junior")
    city: str = Field("Bengaluru", description="Target city", example="Bengaluru")


class SalaryPredictResponse(BaseModel):
    estimated_lpa_min: float
    estimated_lpa_median: float
    estimated_lpa_max: float
    predicted_band: str
    city_factor: float
    experience_multiplier: float
    skill_bonuses: Dict[str, float]
    disclaimer: str


# 3. Skill Gap Analysis
class SkillGapRequest(BaseModel):
    current_skills: List[str] = Field(..., example=["python", "git", "sql"])
    target_role: str = Field(..., example="ML Engineer")
    experience: Optional[str] = Field("junior", example="junior")
    location: Optional[str] = Field("Bengaluru", example="Bengaluru")


class MissingSkillDetail(BaseModel):
    skill: str
    frequency_in_role_pct: float
    salary_premium_lpa: float
    market_status: str
    priority: str  # Critical, High, Medium, Nice-to-have


class SkillGapResponse(BaseModel):
    target_role: str
    role_avg_lpa: float
    role_postings_count: int
    match_percentage: float
    possessed_skills: List[str]
    missing_skills: List[MissingSkillDetail]
    recommended_learning_order: List[str]
    related_roles: List[Dict[str, Any]]


# 4. Career Roadmap Generator
class RoadmapStage(BaseModel):
    stage_number: int
    title: str
    skills_to_learn: List[str]
    why_it_matters: str
    estimated_duration_weeks: int
    recommended_project: str
    practical_exercises: List[str]
    expected_outcome: str


class RoadmapRequest(BaseModel):
    target_role: str = Field(..., example="Data Scientist")
    current_skills: Optional[List[str]] = Field(default_factory=list, example=["python"])


class RoadmapResponse(BaseModel):
    target_role: str
    total_estimated_weeks: int
    stages: List[RoadmapStage]
    fresher_tips: List[str]
    free_resources: List[Dict[str, str]]


# 5. Career Readiness Assessment
class ReadinessRequest(BaseModel):
    skills: List[str] = Field(..., example=["python", "sql", "git"])
    target_role: str = Field(..., example="Backend Developer")
    experience: Optional[str] = Field("junior", example="junior")
    has_projects: Optional[bool] = Field(True, example=True)


class ReadinessResponse(BaseModel):
    readiness_score: int  # 0 to 100
    readiness_level: str  # Ready, Near Ready, Developing, Beginner
    skill_coverage_pct: float
    scoring_breakdown: Dict[str, Any]
    strengths: List[str]
    critical_gaps: List[str]
    recommended_projects: List[str]
    next_steps: List[str]
    transparent_formula: str


# 6. Jobs Explorer
class JobFilterParams(BaseModel):
    city: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    experience: Optional[str] = None
    work_mode: Optional[str] = None
    skill: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    page: int = 1
    page_size: int = 20


# 7. AI Career Assistant
class ChatRequest(BaseModel):
    message: str = Field(..., example="Which skills pay the highest salary in Bengaluru?")
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    suggested_questions: List[str]
    data_sources_used: List[str]
