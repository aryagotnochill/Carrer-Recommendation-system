"""
Career Recommendation System Package
AI-powered career recommendations with ML and LLM
"""

__version__ = "1.0.0"
__author__ = "Career AI Team"
__description__ = "Intelligent career recommendation system using ML and AI"

from data.career_data import (
    get_career_dataset,
    get_skills_taxonomy,
    get_industry_list,
    get_education_options,
    get_experience_levels,
    get_interests
)

from src.model import CareerRecommendationEngine, SkillGapAnalyzer
from src.utils import (
    TextPreprocessor,
    SkillMatcher,
    ContentBasedRecommender,
    DatabaseManager
)
from src.llm_integration import LLMIntegration, MockLLM, get_llm_instance

__all__ = [
    'get_career_dataset',
    'get_skills_taxonomy',
    'get_industry_list',
    'get_education_options',
    'get_experience_levels',
    'get_interests',
    'CareerRecommendationEngine',
    'SkillGapAnalyzer',
    'TextPreprocessor',
    'SkillMatcher',
    'ContentBasedRecommender',
    'DatabaseManager',
    'LLMIntegration',
    'MockLLM',
    'get_llm_instance'
]
