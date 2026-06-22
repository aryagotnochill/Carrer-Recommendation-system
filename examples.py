"""
Example usage of the Career Recommendation System
Demonstrates how to use the system programmatically without Streamlit UI
"""

from data.career_data import get_career_dataset, get_skills_taxonomy
from src.model import CareerRecommendationEngine, SkillGapAnalyzer
from src.llm_integration import get_llm_instance
import json


def example_basic_recommendation():
    """Example 1: Get basic recommendations"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Recommendations")
    print("=" * 60)
    
    # Load data
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    # Create engine
    engine = CareerRecommendationEngine(careers_df, all_skills)
    
    # Define user profile
    user_profile = {
        'skills': ['Python', 'SQL', 'Data Visualization', 'Statistics'],
        'education': 'Bachelor in Computer Science',
        'projects': 'Built a dashboard analyzing sales trends using Python and Tableau',
        'experience_level': 'Internship',
        'interests': ['Data Analysis', 'Machine Learning'],
        'preferred_industry': 'Finance'
    }
    
    print(f"\nUser Profile:")
    print(f"  Skills: {', '.join(user_profile['skills'])}")
    print(f"  Education: {user_profile['education']}")
    print(f"  Experience: {user_profile['experience_level']}")
    
    # Get recommendations
    recommendations = engine.recommend(user_profile, top_n=3)
    
    print(f"\nTop 3 Recommendations:")
    for idx, (_, career) in enumerate(recommendations.iterrows(), 1):
        print(f"\n{idx}. {career['title']}")
        print(f"   Match Score: {career['composite_score']:.1f}%")
        print(f"   Demand: {career['demand_score']}/10")
        print(f"   Salary: ${career['salary_min']:,} - ${career['salary_max']:,}")
        print(f"   Description: {career['description']}")


def example_skill_gap_analysis():
    """Example 2: Analyze skill gaps"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Skill Gap Analysis")
    print("=" * 60)
    
    careers_df = get_career_dataset()
    
    # Select a specific career
    data_scientist_career = careers_df[careers_df['title'] == 'Data Scientist'].iloc[0]
    
    # User skills
    user_skills = ['Python', 'SQL', 'Statistics']
    
    print(f"\nCareer: {data_scientist_career['title']}")
    print(f"Your Skills: {', '.join(user_skills)}")
    print(f"Required Skills: {', '.join(data_scientist_career['required_skills'])}")
    
    # Analyze gap
    gap_analysis = SkillGapAnalyzer.analyze_gaps(
        user_skills,
        data_scientist_career['required_skills'],
        data_scientist_career['nice_to_have']
    )
    
    print(f"\nGap Analysis:")
    print(f"  Readiness Score: {gap_analysis['readiness_score']:.1f}%")
    print(f"  Missing Required Skills: {len(gap_analysis['missing_required'])}")
    print(f"    {', '.join(gap_analysis['missing_required'][:3])}")
    print(f"  Nice-to-Have Missing: {len(gap_analysis['missing_nice'])}")
    print(f"    {', '.join(gap_analysis['missing_nice'][:3])}")
    
    # Learning time estimate
    learning_weeks = SkillGapAnalyzer.estimate_learning_time(
        len(gap_analysis['missing_required'])
    )
    print(f"  Estimated Learning Time: {learning_weeks} weeks ({learning_weeks // 4} months)")
    
    # Learning priorities
    print(f"\n  Learning Priorities:")
    for skill, priority in gap_analysis['learning_priority'][:5]:
        print(f"    - {skill} ({priority})")


def example_with_llm():
    """Example 3: Using LLM for insights"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: LLM-Powered Insights")
    print("=" * 60)
    
    # Initialize LLM (mock for this example)
    llm = get_llm_instance(use_mock=True)
    
    print("\nLLM Type: Mock (for demo)")
    print("Note: Set use_mock=False to use real OpenAI API if you have API key\n")
    
    # Example 1: Career explanation
    explanation = llm.explain_recommendation(
        career_title="Machine Learning Engineer",
        match_score=85.0,
        user_skills=["Python", "Math", "ML Basics"],
        required_skills=["Python", "Machine Learning", "Deep Learning", "Statistics"]
    )
    
    print("1. Career Explanation:")
    print(f"   {explanation}\n")
    
    # Example 2: Learning roadmap
    roadmap = llm.generate_roadmap(
        career_title="Machine Learning Engineer",
        user_skills=["Python"],
        missing_skills=["Deep Learning", "TensorFlow", "Statistics", "Distributed Systems"],
        experience_level="Internship"
    )
    
    print("2. Personalized Learning Roadmap:")
    print(roadmap)
    
    # Example 3: Project suggestions
    projects = llm.suggest_projects(
        career_title="Machine Learning Engineer",
        user_skills=["Python"],
        experience_level="Internship"
    )
    
    print("\n3. Project Suggestions:")
    print(projects)


def example_multiple_profiles():
    """Example 4: Compare recommendations for different profiles"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Multiple User Profiles Comparison")
    print("=" * 60)
    
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    engine = CareerRecommendationEngine(careers_df, all_skills)
    
    # Three different user profiles
    profiles = [
        {
            'name': 'Fresh Graduate',
            'profile': {
                'skills': ['JavaScript', 'CSS', 'HTML'],
                'education': "Bachelor's in CS",
                'projects': 'Personal portfolio website',
                'experience_level': 'Fresher',
                'interests': ['Web Development', 'Design'],
                'preferred_industry': ''
            }
        },
        {
            'name': 'Data Science Student',
            'profile': {
                'skills': ['Python', 'R', 'Statistics', 'SQL'],
                'education': "Master's in Data Science",
                'projects': 'Kaggle competitions',
                'experience_level': 'Internship',
                'interests': ['Machine Learning', 'Data Analysis'],
                'preferred_industry': 'Tech'
            }
        },
        {
            'name': 'Experienced Developer',
            'profile': {
                'skills': ['Python', 'Java', 'Docker', 'Kubernetes', 'AWS', 'CI/CD'],
                'education': "Bachelor's in IT",
                'projects': 'Microservices deployment',
                'experience_level': 'Experienced',
                'interests': ['Cloud Computing', 'DevOps', 'Infrastructure'],
                'preferred_industry': 'Finance'
            }
        }
    ]
    
    for profile_info in profiles:
        name = profile_info['name']
        profile = profile_info['profile']
        
        print(f"\n{name}:")
        print(f"  Skills: {', '.join(profile['skills'])}")
        
        recommendations = engine.recommend(profile, top_n=2)
        
        for idx, (_, career) in enumerate(recommendations.iterrows(), 1):
            print(f"  {idx}. {career['title']} ({career['composite_score']:.1f}% match)")


def example_export_recommendations():
    """Example 5: Export recommendations to JSON"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Export Recommendations")
    print("=" * 60)
    
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    
    engine = CareerRecommendationEngine(careers_df, all_skills)
    
    user_profile = {
        'skills': ['Python', 'SQL', 'Machine Learning'],
        'education': "Bachelor's in IT",
        'projects': 'ML projects on GitHub',
        'experience_level': 'Internship',
        'interests': ['Machine Learning', 'AI'],
        'preferred_industry': ''
    }
    
    recommendations = engine.recommend(user_profile, top_n=3)
    
    # Convert to JSON-serializable format
    export_data = {
        'user_profile': user_profile,
        'recommendations': []
    }
    
    for _, career in recommendations.iterrows():
        export_data['recommendations'].append({
            'title': career['title'],
            'score': float(career['composite_score']),
            'description': career['description'],
            'salary_range': f"${int(career['salary_min'])} - ${int(career['salary_max'])}",
            'demand_score': float(career['demand_score']),
            'industries': career['industry']
        })
    
    # Save to file
    filename = 'sample_recommendations.json'
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"\nRecommendations exported to {filename}")
    print("\nSample JSON output:")
    print(json.dumps(export_data, indent=2)[:500] + "...")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("  CAREER RECOMMENDATION SYSTEM - EXAMPLES")
    print("=" * 60)
    
    try:
        example_basic_recommendation()
        example_skill_gap_analysis()
        example_with_llm()
        example_multiple_profiles()
        example_export_recommendations()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        
        print("\nNext Steps:")
        print("1. Run 'streamlit run app.py' to see the interactive UI")
        print("2. Explore the documentation in docs/ folder")
        print("3. Customize the careers and skills to your liking")
        print("4. Deploy to Streamlit Cloud for public access")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
