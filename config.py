import os
from dataclasses import dataclass
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@dataclass
class DataConfig:
    """Configuration for data generation"""
    num_rows: int = 50
    departments: List[str] = None
    salary_range: Tuple[int, int] = (30000, 150000)
    experience_range: Tuple[int, int] = (0, 30)
    age_range: Tuple[int, int] = (18, 65)

    def __post_init__(self):
        if self.departments is None:
            self.departments = ["Engineering", "Sales", "Marketing", "HR", "Finance"]

@dataclass
class QualityMetrics:
    """Quality metrics for data evaluation"""
    completeness: float = 0.0
    uniqueness: float = 0.0
    statistical_validity: float = 0.0
    overall_score: float = 0.0
    feedback: str = ""
