"""
Source code package for career recommendation system
"""

from . import model
from . import utils
from . import llm_integration
from . import random_forest_model

# Import main classes for easy access
from .model import CareerRecommendationEngine, SkillGapAnalyzer
from .random_forest_model import RandomForestCareerRecommender, EnsembleRecommender
from .utils import DatabaseManager, SkillMatcher, TextPreprocessor

__all__ = [
    'model',
    'utils',
    'llm_integration',
    'random_forest_model',
    'CareerRecommendationEngine',
    'SkillGapAnalyzer',
    'RandomForestCareerRecommender',
    'EnsembleRecommender',
    'DatabaseManager',
    'SkillMatcher',
    'TextPreprocessor'
]
