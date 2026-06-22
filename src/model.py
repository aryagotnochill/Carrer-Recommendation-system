"""
Career Recommendation Model
Combines multiple recommendation techniques for hybrid approach
"""

import pandas as pd
import numpy as np
from src.utils import SkillMatcher, ContentBasedRecommender, TextPreprocessor
from sklearn.preprocessing import MinMaxScaler


class CareerRecommendationEngine:
    """
    Hybrid recommendation engine combining:
    - Content-based filtering (TF-IDF similarity)
    - Skill matching analysis
    - Demand-based ranking
    - Experience level matching
    """
    
    def __init__(self, careers_df, all_skills_list):
        """
        Initialize the recommendation engine
        
        Args:
            careers_df: DataFrame with career data
            all_skills_list: List of all available skills
        """
        self.careers_df = careers_df.copy()
        self.skill_matcher = SkillMatcher(all_skills_list)
        self.content_recommender = ContentBasedRecommender()
        self.scaler = MinMaxScaler()
        self.all_skills = all_skills_list
        
    def normalize_scores(self, scores):
        """
        Normalize scores to 0-100 range
        """
        if len(scores) == 0:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [50] * len(scores)
        
        normalized = [
            ((score - min_score) / (max_score - min_score)) * 100
            for score in scores
        ]
        
        return normalized
    
    def recommend(self, user_profile, top_n=5, verbose=False):
        """
        Generate career recommendations based on user profile
        
        Args:
            user_profile: Dictionary containing:
                - skills: List of user skills
                - education: Education qualification
                - projects: Project description
                - experience_level: Fresher/Internship/Experienced
                - interests: List of interests
                - preferred_industry: Optional industry preference
            
            top_n: Number of recommendations to return
            verbose: Print debug info
            
        Returns:
            DataFrame with recommendations and scores
        """
        
        recommendations = self.careers_df.copy()
        
        # 1. CONTENT-BASED SCORE (TF-IDF Similarity) - Weight: 0.3
        if verbose:
            print("Computing content-based scores...")
        
        content_recommendations = self.content_recommender.recommend(
            user_profile, self.careers_df, top_n=len(self.careers_df)
        )
        
        content_scores = [0] * len(recommendations)
        for idx, row in content_recommendations.iterrows():
            career_idx = recommendations[recommendations['id'] == row['id']].index[0]
            content_scores[career_idx] = row['content_score']
        
        recommendations['content_score'] = content_scores
        
        # 2. SKILL MATCH SCORE - Weight: 0.4
        if verbose:
            print("Computing skill match scores...")
        
        skill_match_scores = []
        for idx, career in recommendations.iterrows():
            match_result = self.skill_matcher.calculate_skill_match(
                user_profile.get('skills', []),
                career['required_skills']
            )
            
            # Base score on percentage match
            match_pct = match_result['match_percentage']
            
            # Bonus for nice-to-have skills
            bonus = 0
            if career['nice_to_have']:
                nice_have_match = len(
                    set([s.lower() for s in user_profile.get('skills', [])]) & 
                    set([s.lower() for s in career['nice_to_have']])
                ) / len(career['nice_to_have'])
                bonus = nice_have_match * 10
            
            skill_score = min(100, match_pct + bonus)
            skill_match_scores.append(skill_score)
        
        recommendations['skill_match_score'] = skill_match_scores
        
        # 3. EXPERIENCE LEVEL MATCH - Weight: 0.15
        if verbose:
            print("Computing experience level match...")
        
        experience_match_scores = []
        user_exp = user_profile.get('experience_level', 'Fresher')
        
        for idx, career in recommendations.iterrows():
            if user_exp in career['career_level']:
                experience_match_scores.append(100)
            elif len(career['career_level']) > 0:
                # Partial score if not exact match
                experience_match_scores.append(70)
            else:
                experience_match_scores.append(50)
        
        recommendations['experience_match_score'] = experience_match_scores
        
        # 4. DEMAND & GROWTH SCORE - Weight: 0.15
        if verbose:
            print("Computing demand scores...")
        
        # Combine demand score and growth trend
        growth_multipliers = {
            'Rapidly Increasing': 1.3,
            'Increasing': 1.15,
            'Stable High': 1.0,
            'Stable': 0.85,
            'Declining': 0.7
        }
        
        demand_scores = []
        for idx, career in recommendations.iterrows():
            base_demand = career['demand_score'] * 10  # Scale to 0-100
            growth_mult = growth_multipliers.get(career['growth_trend'], 1.0)
            demand_score = base_demand * growth_mult
            demand_scores.append(min(100, demand_score))
        
        recommendations['demand_score_normalized'] = demand_scores
        
        # 5. INDUSTRY PREFERENCE MATCH - Weight: 0.05 (bonus)
        if verbose:
            print("Computing industry preference match...")
        
        industry_bonus_scores = []
        preferred_industry = user_profile.get('preferred_industry', '')
        
        for idx, career in recommendations.iterrows():
            if preferred_industry and preferred_industry in career['industry']:
                industry_bonus_scores.append(20)
            else:
                industry_bonus_scores.append(0)
        
        recommendations['industry_bonus'] = industry_bonus_scores
        
        # 6. CALCULATE COMPOSITE SCORE
        if verbose:
            print("Computing composite scores...")
        
        composite_scores = (
            (recommendations['content_score'] * 0.3) +
            (recommendations['skill_match_score'] * 0.4) +
            (recommendations['experience_match_score'] * 0.15) +
            (recommendations['demand_score_normalized'] * 0.15) +
            (recommendations['industry_bonus'] * 0.05)
        )
        
        recommendations['composite_score'] = composite_scores
        
        # Sort by composite score
        recommendations = recommendations.sort_values(
            'composite_score', ascending=False
        )
        
        # Store detailed match results for later display
        recommendations['skill_gap_analysis'] = recommendations.apply(
            lambda x: self.skill_matcher.calculate_skill_match(
                user_profile.get('skills', []),
                x['required_skills']
            ),
            axis=1
        )
        
        if verbose:
            print("\nTop Recommendations:")
            for idx, row in recommendations.head(top_n).iterrows():
                print(f"{row['title']}: {row['composite_score']:.1f}")
        
        return recommendations.head(top_n)
    
    def get_skill_gap_analysis(self, recommendation_row, user_skills):
        """
        Get detailed skill gap analysis for a career
        """
        return self.skill_matcher.calculate_skill_match(
            user_skills,
            recommendation_row['required_skills']
        )
    
    def get_roadmap_context(self, user_profile, recommendation_row):
        """
        Prepare context for LLM to generate personalized roadmap
        
        Args:
            user_profile: User profile dictionary
            recommendation_row: Selected career row
            
        Returns:
            Dictionary with context for LLM prompt
        """
        gap_analysis = self.skill_matcher.calculate_skill_match(
            user_profile.get('skills', []),
            recommendation_row['required_skills']
        )
        
        return {
            'user_skills': user_profile.get('skills', []),
            'target_career': recommendation_row['title'],
            'required_skills': recommendation_row['required_skills'],
            'nice_to_have': recommendation_row.get('nice_to_have', []),
            'missing_skills': gap_analysis['missing_skills'],
            'extra_skills': gap_analysis['extra_skills'],
            'match_percentage': gap_analysis['match_percentage'],
            'experience_level': user_profile.get('experience_level', ''),
            'current_interests': user_profile.get('interests', []),
            'career_description': recommendation_row['description_long'],
            'salary_range': f"${recommendation_row['salary_min']:,} - ${recommendation_row['salary_max']:,}",
            'industries': ', '.join(recommendation_row['industry']),
            'demand_score': recommendation_row['demand_score']
        }
    
    def get_recommendations_summary(self, recommendations_df):
        """
        Get summary statistics of recommendations
        """
        if len(recommendations_df) == 0:
            return None
        
        top_recommendation = recommendations_df.iloc[0]
        
        summary = {
            'top_career': top_recommendation['title'],
            'top_score': top_recommendation['composite_score'],
            'avg_score': recommendations_df['composite_score'].mean(),
            'score_range': (
                recommendations_df['composite_score'].min(),
                recommendations_df['composite_score'].max()
            ),
            'total_recommendations': len(recommendations_df),
            'high_demand_careers': len(
                recommendations_df[recommendations_df['demand_score'] >= 8.0]
            )
        }
        
        return summary


class SkillGapAnalyzer:
    """Detailed skill gap analysis and recommendations"""
    
    @staticmethod
    def analyze_gaps(user_skills, required_skills, nice_to_have_skills):
        """
        Comprehensive gap analysis
        """
        user_skills_lower = set([s.lower() for s in user_skills])
        required_lower = set([s.lower() for s in required_skills])
        nice_lower = set([s.lower() for s in nice_to_have_skills])
        
        # Gap analysis
        missing_required = required_lower - user_skills_lower
        missing_nice = nice_lower - user_skills_lower
        extra = user_skills_lower - required_lower - nice_lower
        
        # Readiness score
        if len(required_lower) > 0:
            readiness = (
                (len(required_lower - missing_required) / len(required_lower)) * 100
            )
        else:
            readiness = 0
        
        return {
            'readiness_score': readiness,
            'missing_required_count': len(missing_required),
            'missing_nice_count': len(missing_nice),
            'missing_required': list(missing_required),
            'missing_nice': list(missing_nice),
            'extra': list(extra),
            'learning_priority': (
                [(skill, 'Critical') for skill in missing_required] +
                [(skill, 'Nice to Have') for skill in missing_nice]
            )
        }
    
    @staticmethod
    def estimate_learning_time(skills_count):
        """
        Estimate time to learn skills (rough estimate)
        """
        # Rough estimates: 1-2 months per major skill
        base_time = 1  # Weeks per skill
        return max(4, skills_count * base_time)  # Minimum 4 weeks


if __name__ == "__main__":
    print("Career Recommendation Engine module loaded successfully")
