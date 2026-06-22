"""
Random Forest-based Career Recommendation Model
Advanced ML approach using scikit-learn's Random Forest classifier
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class RandomForestCareerRecommender:
    """
    Random Forest-based career recommendation system
    Uses ensemble learning for robust predictions
    """
    
    def __init__(self, careers_df, all_skills_list, n_estimators=100):
        """
        Initialize Random Forest recommender
        
        Args:
            careers_df: Career dataset
            all_skills_list: List of all available skills
            n_estimators: Number of trees in forest
        """
        self.careers_df = careers_df.copy()
        self.all_skills = all_skills_list
        self.n_estimators = n_estimators
        
        # Initialize models
        self.classifier = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.regressor = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Train on career data
        self._train_models()
    
    def _extract_features(self, user_profile: Dict) -> np.ndarray:
        """
        Extract features from user profile
        
        Args:
            user_profile: User profile dictionary
            
        Returns:
            Feature vector for prediction
        """
        features = []
        
        # 1. Number of skills
        num_skills = len(user_profile.get('skills', []))
        features.append(num_skills)
        
        # 2. Education level encoding
        education = user_profile.get('education', 'Bachelor')
        education_mapping = {
            '10th': 1, '12th': 2, 'Bachelor': 3, 'Master': 4, 'PhD': 5
        }
        features.append(education_mapping.get(education, 3))
        
        # 3. Experience level
        exp_level = user_profile.get('experience_level', 'Fresher')
        exp_mapping = {'Fresher': 1, 'Internship': 1.5, 'Experienced': 3}
        features.append(exp_mapping.get(exp_level, 1))
        
        # 4. Number of projects
        projects_text = user_profile.get('projects', '')
        num_projects = len(projects_text.split(',')) if projects_text else 0
        features.append(num_projects)
        
        # 5. Number of interests
        num_interests = len(user_profile.get('interests', []))
        features.append(num_interests)
        
        # 6-20. Skill presence (binary for top 15 skills)
        user_skills_lower = [s.lower() for s in user_profile.get('skills', [])]
        for i in range(15):
            if i < len(self.all_skills):
                has_skill = 1 if self.all_skills[i].lower() in user_skills_lower else 0
                features.append(has_skill)
        
        return np.array(features).reshape(1, -1)
    
    def _extract_career_features(self, career: pd.Series) -> np.ndarray:
        """
        Extract features from career row
        
        Args:
            career: Career data series
            
        Returns:
            Feature vector
        """
        features = []
        
        # Number of required skills
        features.append(len(career.get('required_skills', [])))
        
        # Demand score
        features.append(career.get('demand_score', 5))
        
        # Salary range
        sal_min = career.get('salary_min', 0)
        sal_max = career.get('salary_max', 0)
        features.append((sal_min + sal_max) / 2 / 100000)  # Normalize
        
        # Number of industries
        features.append(len(career.get('industry', [])))
        
        # Number of career levels
        features.append(len(career.get('career_level', [])))
        
        # Growth trend encoding
        growth_mapping = {'Stable': 0, 'Moderate Growth': 1, 'High Growth': 2}
        growth = growth_mapping.get(career.get('growth_trend', 'Stable'), 0)
        features.append(growth)
        
        # Nice to have skills count
        features.append(len(career.get('nice_to_have', [])))
        
        # Description length
        desc = career.get('description', '')
        features.append(len(desc.split()) / 100)  # Normalize
        
        return np.array(features).reshape(1, -1)
    
    def _train_models(self):
        """Train Random Forest models on career data"""
        try:
            # Prepare training data
            X = []
            y_classifier = []  # Career ID for classification
            y_regressor = []    # Demand score for regression
            
            for idx, career in self.careers_df.iterrows():
                features = self._extract_career_features(career)
                X.append(features.flatten())
                y_classifier.append(career.get('id', idx))
                y_regressor.append(career.get('demand_score', 5))
            
            X = np.array(X)
            y_classifier = np.array(y_classifier)
            y_regressor = np.array(y_regressor)
            
            # Standardize features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train classifier
            self.classifier.fit(X_scaled, y_classifier)
            
            # Train regressor
            self.regressor.fit(X_scaled, y_regressor)
            
            self.is_trained = True
            
        except Exception as e:
            print(f"Warning: Could not train Random Forest models: {e}")
            self.is_trained = False
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores from trained model
        
        Returns:
            Dictionary of feature names and importance scores
        """
        if not self.is_trained:
            return {}
        
        feature_names = [
            'Num_Skills', 'Education_Level', 'Experience_Level', 
            'Num_Projects', 'Num_Interests',
            'Skill_1', 'Skill_2', 'Skill_3', 'Skill_4', 'Skill_5',
            'Skill_6', 'Skill_7', 'Skill_8', 'Skill_9', 'Skill_10',
            'Skill_11', 'Skill_12', 'Skill_13', 'Skill_14', 'Skill_15'
        ]
        
        importance = self.classifier.feature_importances_
        return {name: imp for name, imp in zip(feature_names, importance)}
    
    def predict_match_score(self, user_profile: Dict, career: pd.Series) -> float:
        """
        Predict match score between user and career using Random Forest
        
        Args:
            user_profile: User profile dictionary
            career: Career series
            
        Returns:
            Match score (0-100)
        """
        if not self.is_trained:
            return 0.0
        
        try:
            # Extract features
            user_features = self._extract_features(user_profile).flatten()
            career_features = self._extract_career_features(career).flatten()
            
            # Combine features
            combined_features = np.concatenate([user_features, career_features])
            combined_features = combined_features.reshape(1, -1)
            
            # Get prediction probabilities
            proba = self.classifier.predict_proba(
                self.scaler.transform(career_features.reshape(1, -1))
            )
            
            # Get regressor prediction
            demand_pred = self.regressor.predict(
                self.scaler.transform(career_features.reshape(1, -1))
            )[0]
            
            # Skill match based on user skills
            user_skills_lower = [s.lower() for s in user_profile.get('skills', [])]
            required_skills_lower = [s.lower() for s in career.get('required_skills', [])]
            
            skill_match = len(set(user_skills_lower) & set(required_skills_lower))
            max_skills = len(required_skills_lower) if required_skills_lower else 1
            skill_ratio = min(skill_match / max_skills, 1.0)
            
            # Combine scores
            base_score = np.mean(proba[0]) * 100 if len(proba[0]) > 0 else 50
            demand_score = (demand_pred / 10) * 100  # Normalize to 0-100
            skill_score = skill_ratio * 100
            
            # Weighted combination
            final_score = (
                0.35 * base_score +
                0.35 * skill_score +
                0.30 * demand_score
            )
            
            return min(max(final_score, 0), 100)
            
        except Exception as e:
            print(f"Error predicting: {e}")
            return 0.0
    
    def recommend(self, user_profile: Dict, top_n: int = 5) -> pd.DataFrame:
        """
        Generate career recommendations using Random Forest
        
        Args:
            user_profile: User profile dictionary
            top_n: Number of recommendations
            
        Returns:
            DataFrame with recommendations and scores
        """
        recommendations = self.careers_df.copy()
        
        # Calculate match scores for each career
        match_scores = []
        for idx, career in recommendations.iterrows():
            score = self.predict_match_score(user_profile, career)
            match_scores.append(score)
        
        recommendations['rf_match_score'] = match_scores
        
        # Sort by score and return top N
        recommendations = recommendations.nlargest(top_n, 'rf_match_score')
        
        return recommendations.reset_index(drop=True)
    
    def predict_success_probability(self, user_profile: Dict, career: pd.Series) -> float:
        """
        Predict probability of success in a career
        
        Args:
            user_profile: User profile
            career: Career row
            
        Returns:
            Success probability (0-1)
        """
        try:
            match_score = self.predict_match_score(user_profile, career)
            return match_score / 100.0
        except:
            return 0.5
    
    def get_career_insights(self, user_profile: Dict) -> Dict:
        """
        Get detailed insights based on Random Forest analysis
        
        Args:
            user_profile: User profile
            
        Returns:
            Dictionary with insights
        """
        insights = {
            'feature_importance': self.get_feature_importance(),
            'user_skill_count': len(user_profile.get('skills', [])),
            'education_level': user_profile.get('education', 'Unknown'),
            'experience_level': user_profile.get('experience_level', 'Fresher'),
            'num_interests': len(user_profile.get('interests', [])),
            'model_trained': self.is_trained
        }
        
        return insights


class EnsembleRecommender:
    """
    Ensemble approach combining Random Forest with traditional methods
    """
    
    def __init__(self, careers_df, all_skills_list, hybrid_engine=None):
        """
        Initialize ensemble recommender
        
        Args:
            careers_df: Career dataset
            all_skills_list: Skills list
            hybrid_engine: Optional hybrid engine to combine with
        """
        self.rf_recommender = RandomForestCareerRecommender(
            careers_df, all_skills_list
        )
        self.hybrid_engine = hybrid_engine
        self.careers_df = careers_df
    
    def recommend(self, user_profile: Dict, top_n: int = 5) -> pd.DataFrame:
        """
        Generate recommendations using ensemble method
        
        Args:
            user_profile: User profile
            top_n: Number of recommendations
            
        Returns:
            DataFrame with combined scores
        """
        # Get Random Forest recommendations
        rf_recs = self.rf_recommender.recommend(user_profile, top_n=len(self.careers_df))
        
        # Get hybrid recommendations if available
        if self.hybrid_engine:
            hybrid_recs = self.hybrid_engine.recommend(user_profile, 
                                                       top_n=len(self.careers_df))
            
            # Merge scores
            rf_recs['hybrid_score'] = 0.0
            for idx, rf_row in rf_recs.iterrows():
                hybrid_match = hybrid_recs[
                    hybrid_recs['title'] == rf_row['title']
                ]
                if not hybrid_match.empty:
                    rf_recs.loc[idx, 'hybrid_score'] = hybrid_match.iloc[0]['composite_score']
            
            # Combine scores
            rf_recs['ensemble_score'] = (
                0.5 * rf_recs['rf_match_score'] +
                0.5 * rf_recs['hybrid_score']
            )
            
            rf_recs = rf_recs.nlargest(top_n, 'ensemble_score')
        else:
            rf_recs['ensemble_score'] = rf_recs['rf_match_score']
            rf_recs = rf_recs.head(top_n)
        
        return rf_recs.reset_index(drop=True)
