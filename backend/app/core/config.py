"""SkillPulse Configuration & Paths."""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillPulse – The Stock Market of Skills"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api"
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    DATA_CSV_PATH: str = os.path.join(BASE_DIR, "data", "job_postings.csv")
    INSIGHTS_JSON_PATH: str = os.path.join(BASE_DIR, "frontend", "data", "insights.json")
    
    CORS_ORIGINS: list[str] = ["*"]

settings = Settings()
