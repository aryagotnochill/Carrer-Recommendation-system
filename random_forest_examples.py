"""
Example: Using Random Forest for Career Recommendations
Demonstrates advanced ML-based recommendations
"""

from src.random_forest_model import RandomForestCareerRecommender, EnsembleRecommender
from src.model import CareerRecommendationEngine
from data.career_data import get_career_dataset, get_skills_taxonomy
import pandas as pd


def example_random_forest_basic():
    """Basic Random Forest recommendations"""
    print("=" * 80)
    print("EXAMPLE 1: Random Forest Career Recommendations (Basic)")
    print("=" * 80)
    
    # Load data
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    # Initialize Random Forest recommender
    rf_recommender = RandomForestCareerRecommender(careers_df, all_skills, n_estimators=100)
    
    # User profile
    user_profile = {
        'skills': ['Python', 'Machine Learning', 'Data Analysis', 'SQL'],
        'education': 'Bachelor',
        'projects': 'ML Project, Data Analysis Dashboard',
        'experience_level': 'Internship',
        'interests': ['AI', 'Data Science', 'Technology'],
        'preferred_industry': 'Technology'
    }
    
    print("\n👤 User Profile:")
    print(f"  Skills: {', '.join(user_profile['skills'])}")
    print(f"  Education: {user_profile['education']}")
    print(f"  Experience: {user_profile['experience_level']}")
    print(f"  Interests: {', '.join(user_profile['interests'])}")
    
    # Get recommendations
    recommendations = rf_recommender.recommend(user_profile, top_n=5)
    
    print("\n🎯 Top 5 Random Forest Recommendations:")
    for idx, (_, career) in enumerate(recommendations.iterrows(), 1):
        print(f"\n{idx}. {career['title']}")
        print(f"   Match Score: {career['rf_match_score']:.1f}%")
        print(f"   Demand: {career['demand_score']}/10")
        print(f"   Salary: ${career['salary_min']:,} - ${career['salary_max']:,}")
        print(f"   Required Skills: {', '.join(career['required_skills'][:3])}...")


def example_feature_importance():
    """Show feature importance from Random Forest model"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Feature Importance Analysis")
    print("=" * 80)
    
    # Load data
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    # Initialize model
    rf_recommender = RandomForestCareerRecommender(careers_df, all_skills)
    
    # Get feature importance
    importance = rf_recommender.get_feature_importance()
    
    print("\n📊 Feature Importance Ranking:")
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feature, score in sorted_features[:10]:
        bar = '█' * int(score * 50)
        print(f"  {feature:20} {bar} {score:.4f}")
    
    print("\nInterpretation: Higher scores = more important for predictions")


def example_ensemble_method():
    """Ensemble approach combining Random Forest with hybrid method"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Ensemble Recommendations (RF + Hybrid)")
    print("=" * 80)
    
    # Load data
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    # Initialize both engines
    hybrid_engine = CareerRecommendationEngine(careers_df, all_skills)
    ensemble = EnsembleRecommender(careers_df, all_skills, hybrid_engine)
    
    # User profile
    user_profile = {
        'skills': ['Python', 'JavaScript', 'React', 'Node.js'],
        'education': 'Bachelor',
        'projects': 'Web App, Mobile App',
        'experience_level': 'Experienced',
        'interests': ['Web Development', 'Startups'],
        'preferred_industry': 'Technology'
    }
    
    print("\n👤 User Profile:")
    print(f"  Skills: {', '.join(user_profile['skills'])}")
    print(f"  Experience: {user_profile['experience_level']}")
    
    # Get ensemble recommendations
    recommendations = ensemble.recommend(user_profile, top_n=5)
    
    print("\n🎯 Ensemble Recommendations (RF + Hybrid):")
    for idx, (_, career) in enumerate(recommendations.iterrows(), 1):
        print(f"\n{idx}. {career['title']}")
        if 'rf_match_score' in career:
            print(f"   RF Score:      {career['rf_match_score']:.1f}%")
        if 'hybrid_score' in career:
            print(f"   Hybrid Score:  {career['hybrid_score']:.1f}%")
        if 'ensemble_score' in career:
            print(f"   Ensemble:      {career['ensemble_score']:.1f}%")


def example_success_probability():
    """Predict success probability for specific career"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Success Probability Prediction")
    print("=" * 80)
    
    # Load data
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    # Initialize model
    rf_recommender = RandomForestCareerRecommender(careers_df, all_skills)
    
    # Multiple user profiles
    profiles = [
        {
            'name': 'Fresh Graduate in Data',
            'skills': ['Python', 'Statistics', 'SQL'],
            'education': 'Bachelor',
            'projects': 'Data Analysis Project',
            'experience_level': 'Fresher',
            'interests': ['Data Science', 'Analytics'],
            'preferred_industry': 'Technology'
        },
        {
            'name': 'Experienced Full Stack Dev',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'Docker', 'AWS'],
            'education': 'Bachelor',
            'projects': 'Web App, Mobile App, Microservices',
            'experience_level': 'Experienced',
            'interests': ['Web Development', 'Cloud'],
            'preferred_industry': 'Technology'
        },
        {
            'name': 'Product Manager',
            'skills': ['Business Analysis', 'Product Strategy', 'SQL'],
            'education': 'Master',
            'projects': 'Product Launch, Market Research',
            'experience_level': 'Experienced',
            'interests': ['Product Management', 'Business'],
            'preferred_industry': 'Technology'
        }
    ]
    
    careers_to_test = ['Data Scientist', 'Backend Developer', 'Product Manager']
    
    print("\n📈 Success Probability Analysis:\n")
    
    for profile in profiles:
        print(f"\n{profile['name']}:")
        print(f"  Skills: {', '.join(profile['skills'])}")
        
        for career_title in careers_to_test:
            career_match = careers_df[careers_df['title'] == career_title]
            if not career_match.empty:
                career = career_match.iloc[0]
                success_prob = rf_recommender.predict_success_probability(profile, career)
                prob_percent = success_prob * 100
                
                # Visual representation
                bar_len = int(prob_percent / 10)
                bar = '█' * bar_len + '░' * (10 - bar_len)
                print(f"    {career_title:20} {bar} {prob_percent:.1f}%")


def example_model_insights():
    """Get detailed model insights"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Model Insights")
    print("=" * 80)
    
    # Load data
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    # Initialize model
    rf_recommender = RandomForestCareerRecommender(careers_df, all_skills, n_estimators=100)
    
    user_profile = {
        'skills': ['Python', 'Data Analysis', 'SQL'],
        'education': 'Master',
        'projects': 'Data Pipeline, Analytics',
        'experience_level': 'Experienced',
        'interests': ['Data Science', 'AI'],
        'preferred_industry': 'Technology'
    }
    
    # Get insights
    insights = rf_recommender.get_career_insights(user_profile)
    
    print("\n🔍 User Profile Insights:")
    print(f"  Skill Count: {insights['user_skill_count']}")
    print(f"  Education: {insights['education_level']}")
    print(f"  Experience: {insights['experience_level']}")
    print(f"  Interests: {insights['num_interests']}")
    print(f"  Model Trained: {'✓' if insights['model_trained'] else '✗'}")


if __name__ == "__main__":
    print("\n🤖 Random Forest Career Recommendation System - Examples\n")
    
    # Run all examples
    example_random_forest_basic()
    example_feature_importance()
    example_ensemble_method()
    example_success_probability()
    example_model_insights()
    
    print("\n" + "=" * 80)
    print("✅ All examples completed successfully!")
    print("=" * 80 + "\n")
