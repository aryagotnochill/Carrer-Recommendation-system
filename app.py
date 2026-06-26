"""
Career Recommendation System - Streamlit App
Production-ready UI for career recommendations
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data.career_data import (
    get_career_dataset, get_skills_taxonomy, get_industry_list,
    get_education_options, get_experience_levels, get_interests
)
from src.model import CareerRecommendationEngine, SkillGapAnalyzer
from src.utils import DatabaseManager, SkillMatcher, TextPreprocessor
from src.llm_integration import get_llm_instance, MockLLM
import json
from datetime import datetime

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Career Recommendation System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STYLING
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        color: #1f77b4;
        font-weight: bold;
        margin-bottom: 1em;
    }
    .subheader {
        font-size: 1.5em;
        color: #333;
        font-weight: bold;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1em;
        border-radius: 0.5em;
        margin: 0.5em 0;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5em;
        border-radius: 0.5em;
        margin: 1em 0;
    }
    .skill-gap {
        background-color: #fff3cd;
        padding: 1em;
        border-radius: 0.5em;
        margin: 0.5em 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.logged_in = False
    st.session_state.recommendations = None
    st.session_state.user_profile = None
    st.session_state.llm_available = False

# ============================================================================
# INITIALIZE COMPONENTS
# ============================================================================

@st.cache_resource
def load_data():
    """Load and cache career dataset"""
    careers_df = get_career_dataset()
    skills_taxonomy = get_skills_taxonomy()
    all_skills = [skill for skills in skills_taxonomy.values() for skill in skills]
    return careers_df, skills_taxonomy, all_skills

@st.cache_resource
def initialize_engine(careers_df, all_skills):
    """Initialize recommendation engine"""
    return CareerRecommendationEngine(careers_df, all_skills)

@st.cache_resource
def initialize_database():
    """Initialize database manager"""
    return DatabaseManager('database/career_app.db')

# Load data
careers_df, skills_taxonomy, all_skills = load_data()
engine = initialize_engine(careers_df, all_skills)
db_manager = initialize_database()

# Ensure a guest user exists for persistence
if st.session_state.user_id is None:
    st.session_state.user_id = db_manager.get_or_create_guest_user()

# Load saved profile for the guest user, if any
if st.session_state.user_profile is None and st.session_state.user_id is not None:
    saved_profile = db_manager.get_user_profile(st.session_state.user_id)
    if saved_profile:
        st.session_state.user_profile = saved_profile
        st.info("Loaded saved profile from the database.")

# Initialize LLM (use mock if no API key)
llm = get_llm_instance(use_mock=True)  # Set to False if you have API key
if not isinstance(llm, MockLLM):
    st.session_state.llm_available = True

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def flatten_skills_taxonomy():
    """Flatten skills taxonomy for easy access"""
    return [skill for skills in skills_taxonomy.values() for skill in skills]

def display_recommendation_card(career, score, position=1):
    """Display a recommendation card"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1em; border-left: 4px solid #667eea; border-radius: 0.5em;">
            <div style="font-size: 1.3em; font-weight: bold; color: #333;">{position}. {career['title']}</div>
            <div style="color: #666; margin: 0.5em 0;">{career['description']}</div>
            <div style="color: #888; font-size: 0.9em;">
                💰 ${career['salary_min']:,} - ${career['salary_max']:,} | 
                📈 Demand: {career['demand_score']}/10 | 
                {career['growth_trend']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Score display
        fig = go.Figure(data=[
            go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': f"Match %"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#667eea"},
                    'steps': [
                        {'range': [0, 50], 'color': "#f0f0f0"},
                        {'range': [50, 100], 'color': "#e0e0e0"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 2},
                        'thickness': 0.75,
                        'value': 100
                    }
                },
                number={'valueformat': '.0f'}
            )
        ])
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

def display_skills_chart(user_skills, required_skills):
    """Display skill match visualization"""
    match_data = {
        'Matched': len(set([s.lower() for s in user_skills]) & set([s.lower() for s in required_skills])),
        'Missing': len(set([s.lower() for s in required_skills]) - set([s.lower() for s in user_skills])),
        'Extra': len(set([s.lower() for s in user_skills]) - set([s.lower() for s in required_skills]))
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(match_data.keys()),
            y=list(match_data.values()),
            marker_color=['#2ecc71', '#e74c3c', '#3498db'],
            text=list(match_data.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Skill Match Breakdown",
        xaxis_title="Skill Status",
        yaxis_title="Count",
        height=300,
        showlegend=False
    )
    
    return fig

def display_demands_chart(recommendations_df):
    """Display career demand comparison"""
    chart_data = recommendations_df[['title', 'demand_score']].copy()
    fig = px.bar(
        chart_data,
        y='title',
        x='demand_score',
        orientation='h',
        title='Career Demand Score Comparison',
        labels={'demand_score': 'Demand Score (0-10)', 'title': 'Career'},
        color='demand_score',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=300, showlegend=False)
    return fig

def display_salary_chart(recommendations_df):
    """Display salary ranges"""
    fig = go.Figure()
    
    salary_data = recommendations_df[['title', 'salary_min', 'salary_max']].copy()
    
    for idx, row in salary_data.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['salary_min'], row['salary_max']],
            y=[row['title'], row['title']],
            mode='lines+markers',
            line=dict(width=20, color='#667eea'),
            marker=dict(size=10),
            hovertemplate=f"{row['title']}<br>Range: ${row['salary_min']:,} - ${row['salary_max']:,}<extra></extra>"
        ))
    
    fig.update_layout(
        title='Salary Range Comparison',
        xaxis_title='Annual Salary ($)',
        yaxis_title='Career',
        height=300,
        showlegend=False,
        hovermode='y unified'
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header
    st.markdown('<div class="main-header">🚀 Career Recommendation System</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    **Discover Your Ideal Career Path** 
    
    Answer a few questions about your skills, experience, and interests to get 
    personalized career recommendations with detailed roadmaps and skill gap analysis.
    """)
    
    # ========================================================================
    # SIDEBAR - INPUT COLLECTION
    # ========================================================================
    
    with st.sidebar:
        st.markdown("### 📝 Your Profile")
        
        # Skills
        st.markdown("#### Skills")
        skills_input_method = st.radio("How would you like to input skills?", 
                                       ["Select from list", "Free text", "Both"],
                                       key="skills_input_method")
        
        selected_skills = []
        
        if skills_input_method in ["Select from list", "Both"]:
            st.markdown("**Select Skills:**")
            for category, skills in skills_taxonomy.items():
                with st.expander(category, expanded=False):
                    selected_skills.extend(st.multiselect(
                        f"Select {category}",
                        skills,
                        key=f"skills_category_{category}",
                        label_visibility="collapsed"
                    ))
        
        if skills_input_method in ["Free text", "Both"]:
            free_text_skills = st.text_area(
                "Or describe your skills in your own words:",
                placeholder="E.g., I know Python, SQL, and have experience with machine learning...",
                key="free_text_skills"
            )
            
            if free_text_skills:
                # Extract skills from text
                skill_matcher = SkillMatcher(all_skills)
                extracted = skill_matcher.extract_skills_from_text(free_text_skills)
                if extracted:
                    st.info(f"Extracted skills: {', '.join(extracted[:5])}")
                    selected_skills.extend(extracted)
        
        selected_skills = list(set(selected_skills))  # Remove duplicates
        st.write(f"**Selected Skills ({len(selected_skills)}):**")
        if selected_skills:
            st.success(", ".join(selected_skills[:10]) + 
                      (f"... +{len(selected_skills)-10} more" if len(selected_skills) > 10 else ""))
        
        st.divider()
        
        # Education
        st.markdown("#### Education")
        education_level = st.selectbox(
            "Highest Education",
            list(get_education_options().keys()),
            key="education_level"
        )
        
        education_branch = None
        if education_level in get_education_options():
            education_branch = st.selectbox(
                "Branch/Field",
                get_education_options()[education_level],
                key="education_branch"
            )
        
        st.divider()
        
        # Experience Level
        st.markdown("#### Experience Level")
        experience_level = st.radio(
            "Your Experience",
            list(get_experience_levels().keys()),
            key="experience_level"
        )
        st.caption(get_experience_levels()[experience_level])
        
        st.divider()
        
        # Interests
        st.markdown("#### Interests")
        interests = st.multiselect(
            "Select your interests:",
            get_interests(),
            key="interests"
        )
        
        st.divider()
        
        # Projects
        st.markdown("#### Projects")
        projects_text = st.text_area(
            "Describe your projects/experience:",
            placeholder="E.g., Built a recommendation system using Python and ML...",
            height=100,
            key="projects_text"
        )
        
        st.divider()
        
        # Industry Preference
        st.markdown("#### Preferred Industry")
        preferred_industry = st.selectbox(
            "Optional - Select preferred industry:",
            [""] + get_industry_list(),
            key="preferred_industry"
        )
        
        st.divider()
        
        # Get Recommendations Button
        get_recommendations = st.button(
            "🎯 Get Recommendations",
            use_container_width=True,
            key="get_recommendations_button",
            type="primary"
        )
    
    # ========================================================================
    # MAIN CONTENT AREA
    # ========================================================================
    
    if get_recommendations:
        # Prepare user profile
        user_profile = {
            'skills': selected_skills,
            'education': f"{education_level} - {education_branch}" if education_branch else education_level,
            'projects': projects_text,
            'experience_level': experience_level,
            'interests': interests,
            'preferred_industry': preferred_industry
        }
        
        st.session_state.user_profile = user_profile
        
        # Store recommendations
        with st.spinner("🔍 Analyzing your profile and computing recommendations..."):
            recommendations = engine.recommend(user_profile, top_n=5, verbose=False)
            st.session_state.recommendations = recommendations
        
        st.success("✅ Analysis complete! Check the tabs below for your personalized insights.")
    
    # ========================================================================
    # DISPLAY RESULTS IN TABS
    # ========================================================================
    
    if st.session_state.recommendations is not None:
        recommendations = st.session_state.recommendations
        user_profile = st.session_state.user_profile
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📊 Recommendations", "🎯 Skill Gap Analysis", "🛣️ Learning Roadmap", 
             "📈 Career Insights", "💡 Projects", "📋 Summary"]
        )
        
        # ====================================================================
        # TAB 1: RECOMMENDATIONS
        # ====================================================================
        
        with tab1:
            st.markdown('<div class="subheader">Top Career Recommendations</div>', 
                       unsafe_allow_html=True)
            
            # Display metric cards
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Top Match Career",
                    recommendations.iloc[0]['title']
                )
                st.caption(f"{recommendations.iloc[0]['composite_score']:.1f}% match")
            
            with col2:
                st.metric(
                    "Average Match Score",
                    f"{recommendations['composite_score'].mean():.1f}%"
                )
            
            with col3:
                st.metric(
                    "High Demand Careers",
                    len(recommendations[recommendations['demand_score'] >= 8.0])
                )
            
            st.divider()
            
            # Display recommendation cards
            for idx, (_, career) in enumerate(recommendations.iterrows(), 1):
                display_recommendation_card(career, career['composite_score'], idx)
                
                with st.expander(f"ℹ️ Details - {career['title']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Required Skills:**")
                        st.write(", ".join(career['required_skills']))
                        
                        st.markdown("**Nice to Have:**")
                        st.write(", ".join(career['nice_to_have']))
                    
                    with col2:
                        st.markdown("**Industries:**")
                        st.write(", ".join(career['industry']))
                        
                        st.markdown("**Career Levels:**")
                        st.write(", ".join(career['career_level']))
                    
                    st.markdown("**Full Description:**")
                    st.write(career['description_long'])
                    
                    # LLM Explanation
                    if st.session_state.llm_available or True:  # Always show for demo
                        st.markdown("**AI-Generated Explanation:**")
                        explanation = llm.explain_recommendation(
                            career['title'],
                            career['composite_score'],
                            user_profile['skills'],
                            career['required_skills']
                        )
                        st.info(explanation)
            
            st.divider()
            st.markdown('<div class="subheader">📊 Career Comparison Graphs</div>', 
                       unsafe_allow_html=True)
            
            # Row 1: Demand and Salary
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(
                    display_demands_chart(recommendations),
                    use_container_width=True,
                    key="demand_chart_tab1"
                )
            
            with col2:
                st.plotly_chart(
                    display_salary_chart(recommendations),
                    use_container_width=True,
                    key="salary_chart_tab1"
                )
            
            # Row 2: Match Scores Comparison
            col1, col2 = st.columns(2)
            
            with col1:
                score_df = recommendations[['title', 'composite_score']].head(10).sort_values('composite_score', ascending=True)
                fig_scores = px.bar(
                    score_df,
                    y='title',
                    x='composite_score',
                    orientation='h',
                    title='Career Match Scores',
                    labels={'composite_score': 'Match Score (%)', 'title': 'Career'},
                    color='composite_score',
                    color_continuous_scale='RdYlGn'
                )
                fig_scores.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_scores, use_container_width=True, key="score_chart_tab1")
            
            with col2:
                # Industry distribution
                industry_counts = {}
                for industries in recommendations['industry']:
                    for ind in industries:
                        industry_counts[ind] = industry_counts.get(ind, 0) + 1
                
                industry_df = pd.DataFrame(
                    list(industry_counts.items()),
                    columns=['Industry', 'Count']
                ).sort_values('Count', ascending=False)
                
                fig_industry = px.pie(
                    industry_df,
                    values='Count',
                    names='Industry',
                    title='Career Distribution by Industry'
                )
                fig_industry.update_layout(height=300)
                st.plotly_chart(fig_industry, use_container_width=True, key="industry_chart_tab1")
            
            # Row 3: Growth Trends and Career Levels
            col1, col2 = st.columns(2)
            
            with col1:
                growth_data = recommendations.groupby('growth_trend').size().reset_index(name='count')
                fig_growth = px.bar(
                    growth_data,
                    x='growth_trend',
                    y='count',
                    title='Growth Trend Distribution',
                    labels={'growth_trend': 'Growth Trend', 'count': 'Count'},
                    color='growth_trend',
                    text='count'
                )
                fig_growth.update_layout(height=300, showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig_growth, use_container_width=True, key="growth_chart_tab1")
            
            with col2:
                # Career level distribution
                career_levels = {}
                for levels in recommendations['career_level']:
                    for level in levels:
                        career_levels[level] = career_levels.get(level, 0) + 1
                
                level_df = pd.DataFrame(
                    list(career_levels.items()),
                    columns=['Level', 'Count']
                )
                
                fig_levels = px.bar(
                    level_df,
                    x='Level',
                    y='Count',
                    title='Recommended Career Levels',
                    labels={'Level': 'Career Level', 'Count': 'Count'},
                    color='Level',
                    text='Count'
                )
                fig_levels.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig_levels, use_container_width=True, key="level_chart_tab1")
        
        # ====================================================================
        # TAB 2: SKILL GAP ANALYSIS
        # ====================================================================
        
        with tab2:
            st.markdown('<div class="subheader">Skill Gap Analysis</div>', 
                       unsafe_allow_html=True)
            
            # Select career to analyze
            selected_career_idx = st.selectbox(
                "Select a career to analyze in detail:",
                range(len(recommendations)),
                format_func=lambda x: recommendations.iloc[x]['title'],
                key="career_select_gap"
            )
            
            selected_career = recommendations.iloc[selected_career_idx]
            gap_analysis = selected_career['skill_gap_analysis']
            
            # Display gap analysis
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Match Percentage", f"{gap_analysis['match_percentage']:.1f}%")
            
            with col2:
                st.metric("Skills Matched", f"{gap_analysis['matched_count']} of {gap_analysis['total_required']}")
            
            with col3:
                st.metric("Skills to Learn", len(gap_analysis['missing_skills']))
            
            st.divider()
            
            # Skills visualization
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(
                    display_skills_chart(user_profile['skills'], 
                                        selected_career['required_skills']),
                    use_container_width=True,
                    key="skills_chart_tab2"
                )
            
            with col2:
                st.markdown("**Your Current Skills:**")
                if user_profile['skills']:
                    for skill in user_profile['skills']:
                        st.success(f"✅ {skill}")
                else:
                    st.info("No skills provided")
            
            st.divider()
            
            # Missing skills
            if gap_analysis['missing_skills']:
                st.markdown("**Critical Skills to Learn:**")
                with st.container():
                    for i, skill in enumerate(gap_analysis['missing_skills'][:5], 1):
                        st.warning(f"❌ {i}. {skill}", icon="⚠️")
                
                if len(gap_analysis['missing_skills']) > 5:
                    st.info(f"... and {len(gap_analysis['missing_skills']) - 5} more skills")
            
            # Learning readiness
            readiness_score = SkillGapAnalyzer.analyze_gaps(
                user_profile['skills'],
                selected_career['required_skills'],
                selected_career['nice_to_have']
            )['readiness_score']
            
            st.divider()
            st.markdown("**Readiness Assessment:**")
            
            if readiness_score >= 80:
                st.success("🎉 You're ready! Minimal skills needed.")
            elif readiness_score >= 60:
                st.info("🚀 Good foundation. Focus on 2-3 key skills.")
            elif readiness_score >= 40:
                st.warning("⏳ Moderate gap. Plan 2-3 months of learning.")
            else:
                st.error("📚 Significant learning curve. Plan 3-4 months of focused study.")
            
            estimated_weeks = SkillGapAnalyzer.estimate_learning_time(
                len(gap_analysis['missing_skills'])
            )
            st.info(f"**Estimated Learning Time:** {estimated_weeks} weeks ({estimated_weeks//4} months)")
        
        # ====================================================================
        # TAB 3: LEARNING ROADMAP
        # ====================================================================
        
        with tab3:
            st.markdown('<div class="subheader">Personalized Learning Roadmap</div>', 
                       unsafe_allow_html=True)
            
            # Select career for roadmap
            selected_career_idx = st.selectbox(
                "Select a career for roadmap:",
                range(len(recommendations)),
                format_func=lambda x: recommendations.iloc[x]['title'],
                key="career_select_roadmap"
            )
            
            selected_career = recommendations.iloc[selected_career_idx]
            gap_analysis = selected_career['skill_gap_analysis']
            
            # Generate roadmap
            with st.spinner("🤖 Generating personalized roadmap..."):
                roadmap = llm.generate_roadmap(
                    selected_career['title'],
                    user_profile['skills'],
                    gap_analysis['missing_skills'],
                    user_profile['experience_level']
                )
            
            st.markdown(roadmap)
            
            # Export option
            if st.button("📥 Copy Roadmap to Clipboard"):
                st.success("Roadmap copied! (Note: Copy to clipboard in real environment)")
        
        # ====================================================================
        # TAB 4: CAREER INSIGHTS
        # ====================================================================
        
        with tab4:
            st.markdown('<div class="subheader">Career Market Insights</div>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Demand Scores**")
                st.plotly_chart(
                    display_demands_chart(recommendations),
                    use_container_width=True,
                    key="demand_chart_tab4"
                )
            
            with col2:
                st.markdown("**Salary Ranges**")
                st.plotly_chart(
                    display_salary_chart(recommendations),
                    use_container_width=True,
                    key="salary_chart_tab4"
                )
            
            st.divider()
            
            # Career growth trends
            st.markdown("**Career Growth Trends**")
            
            growth_data = recommendations.groupby('growth_trend').size().reset_index(name='count')
            if len(growth_data) > 0:
                fig = px.bar(
                    growth_data,
                    x='growth_trend',
                    y='count',
                    title='Growth Trend Distribution',
                    labels={'growth_trend': 'Growth Trend', 'count': 'Number of Careers'},
                    color='growth_trend'
                )
                st.plotly_chart(fig, use_container_width=True, key="growth_trend_chart_tab4")
        
        # ====================================================================
        # TAB 5: PROJECT SUGGESTIONS
        # ====================================================================
        
        with tab5:
            st.markdown('<div class="subheader">Suggested Projects to Build</div>', 
                       unsafe_allow_html=True)
            
            selected_career_idx = st.selectbox(
                "Select a career for project suggestions:",
                range(len(recommendations)),
                format_func=lambda x: recommendations.iloc[x]['title'],
                key="career_select_projects"
            )
            
            selected_career = recommendations.iloc[selected_career_idx]
            gap_analysis = selected_career['skill_gap_analysis']
            
            st.info(f"📌 Project suggestions for **{selected_career['title']}**")
            
            with st.spinner("🔧 Generating project ideas..."):
                projects = llm.suggest_projects(
                    selected_career['title'],
                    user_profile['skills'],
                    user_profile['experience_level']
                )
            
            st.markdown(projects)
            
            st.divider()
            
            st.markdown("**Why Projects Matter:**")
            st.markdown("""
            - 📁 Build a portfolio to showcase skills
            - 🔗 Create GitHub projects for recruiters to see
            - 💡 Learn by doing - most effective learning method
            - 🎯 Demonstrate practical application of skills
            - 📈 Stand out in competitive job market
            """)
        
        # ====================================================================
        # TAB 6: SUMMARY
        # ====================================================================
        
        with tab6:
            st.markdown('<div class="subheader">Your Profile Summary</div>', 
                       unsafe_allow_html=True)
            
            # Profile Info
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Profile Details:**")
                st.json({
                    "Skills": user_profile['skills'],
                    "Education": user_profile['education'],
                    "Experience": user_profile['experience_level'],
                    "Interests": user_profile['interests']
                })
            
            with col2:
                st.markdown("**Top Recommendations:**")
                for idx, rec in enumerate(recommendations.head(3).iterrows(), 1):
                    _, career = rec
                    st.markdown(f"{idx}. **{career['title']}** - {career['composite_score']:.1f}% match")
            
            st.divider()
            
            # Download report
            st.markdown("**Export Options:**")
            
            if st.button("📄 Generate PDF Report", use_container_width=True):
                st.info("PDF generation would require additional libraries (reportlab, fpdf2). Check 'Bonus Features' section in main code.")
            
            if st.button("💾 Save My Profile", use_container_width=True):
                if st.session_state.user_id is not None and user_profile:
                    profile_saved = db_manager.save_user_profile(st.session_state.user_id, user_profile)
                    rec_saved = True
                    for _, career in recommendations.head(5).iterrows():
                        if not db_manager.save_recommendation(
                            st.session_state.user_id,
                            career['title'],
                            float(career['composite_score'])
                        ):
                            rec_saved = False
                    if profile_saved and rec_saved:
                        st.success("Profile and recent recommendations saved successfully.")
                    elif profile_saved:
                        st.warning("Profile saved, but recommendation history could not be fully saved.")
                    else:
                        st.error("Failed to save profile.")
                else:
                    st.warning("No profile data available to save.")
            
            # Career comparison
            st.divider()
            st.markdown("**Career Comparison Table:**")
            
            comparison_df = recommendations[[
                'title', 'demand_score', 'salary_min', 'salary_max', 
                'composite_score', 'growth_trend'
            ]].copy()
            
            comparison_df.columns = [
                'Career', 'Demand Score', 'Min Salary', 'Max Salary', 
                'Match Score', 'Growth Trend'
            ]
            
            st.dataframe(comparison_df, use_container_width=True)
    
    else:
        # Initial state - no recommendations yet
        st.info("👈 Fill in your profile on the left sidebar and click 'Get Recommendations' to get started!")
        
        # Show some example careers
        st.markdown("### 🌟 Sample Careers in Our System")
        
        sample_careers = careers_df.head(4)
        cols = st.columns(2)
        
        for idx, (_, career) in enumerate(sample_careers.iterrows()):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"#### {career['title']}")
                    st.write(f"**Description:** {career['description']}")
                    st.write(f"**Salary Range:** ${career['salary_min']:,} - ${career['salary_max']:,}")
                    st.write(f"**Demand Score:** {career['demand_score']}/10")
                    st.write(f"**Key Skills:** {', '.join(career['required_skills'][:3])}...")
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **About This System:**
        
        This is an AI-powered career recommendation engine that uses machine learning 
        to match your profile with ideal careers.
        """)
    
    with col2:
        st.markdown("""
        **How It Works:**
        
        - Analyzes your skills and experience
        - Compares against 12+ career profiles
        - Generates personalized insights
        - Provides learning roadmaps
        """)
    
    with col3:
        st.markdown("""
        **Technologies Used:**
        
        - Streamlit (UI)
        - Scikit-learn (ML)
        - OpenAI GPT (AI)
        - Plotly (Visualizations)
        """)


if __name__ == "__main__":
    main()
