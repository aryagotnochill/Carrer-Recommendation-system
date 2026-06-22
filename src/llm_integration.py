"""
LLM Integration Module
Handles OpenAI API calls for career insights, explanations, and roadmaps
"""

import os
from typing import Dict, List, Optional


class LLMIntegration:
    """Integration with OpenAI API or similar LLM service"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM integration
        
        Args:
            api_key: OpenAI API key (or get from environment variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY', '')
        self.model = "gpt-3.5-turbo"  # Or gpt-4 for better results
        self.client = None
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            print("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.client is not None and bool(self.api_key)
    
    def call_api(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> Optional[str]:
        """
        Call LLM API
        
        Args:
            prompt: The prompt to send
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            LLM response or None if error
        """
        if not self.is_available():
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a career advisor expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return None
    
    def explain_recommendation(self, career_title: str, 
                              match_score: float,
                              user_skills: List[str],
                              required_skills: List[str]) -> Optional[str]:
        """
        Generate explanation for why this career is recommended
        
        Args:
            career_title: The career being recommended
            match_score: The match percentage
            user_skills: User's current skills
            required_skills: Career's required skills
            
        Returns:
            Explanation text
        """
        prompt = f"""
        Based on the following information, provide a brief (2-3 sentences) 
        personalized explanation for why '{career_title}' is a good career 
        recommendation for this person.
        
        Match Score: {match_score:.1f}%
        User's Skills: {', '.join(user_skills) if user_skills else 'No skills provided'}
        Required Skills for {career_title}: {', '.join(required_skills)}
        
        Make the explanation encouraging and specific to their profile.
        """
        
        return self.call_api(prompt, temperature=0.7, max_tokens=300)
    
    def generate_roadmap(self, career_title: str,
                        user_skills: List[str],
                        missing_skills: List[str],
                        experience_level: str) -> Optional[str]:
        """
        Generate a personalized learning roadmap
        
        Args:
            career_title: Target career
            user_skills: Current skills
            missing_skills: Skills to learn
            experience_level: User's experience level
            
        Returns:
            Roadmap text
        """
        prompt = f"""
        Create a concise 3-month learning roadmap (5-7 bullet points) for someone who wants 
        to become a {career_title}.
        
        Their current level: {experience_level}
        Their existing skills: {', '.join(user_skills) if user_skills else 'Beginner level'}
        Key skills to learn: {', '.join(missing_skills[:5]) if missing_skills else 'Check job listings'}
        
        Include:
        - Week-by-week breakdown
        - Specific tools/technologies to master
        - Projects/portfolio items to build
        - Learning resources recommendation
        
        Keep it practical and achievable.
        """
        
        return self.call_api(prompt, temperature=0.7, max_tokens=600)
    
    def suggest_projects(self, career_title: str,
                        user_skills: List[str],
                        experience_level: str) -> Optional[str]:
        """
        Suggest projects to build portfolio
        
        Args:
            career_title: Target career
            user_skills: Current skills
            experience_level: User's level
            
        Returns:
            Project suggestions
        """
        prompt = f"""
        Suggest 3-4 specific projects that would help someone transition to a {career_title} role.
        
        Their current skills: {', '.join(user_skills) if user_skills else 'Beginner'}
        Experience level: {experience_level}
        
        For each project, briefly mention:
        - Project name
        - Key skills it develops
        - Why it matters for {career_title}
        - Estimated time (days/weeks)
        
        Make suggestions progressively challenging.
        """
        
        return self.call_api(prompt, temperature=0.7, max_tokens=500)
    
    def extract_skills_from_description(self, description: str) -> Optional[List[str]]:
        """
        Extract and suggest skills from user's project description
        
        Args:
            description: User's project/experience description
            
        Returns:
            List of identified skills
        """
        prompt = f"""
        From the following project/experience description, extract the top 5-10 technical 
        skills mentioned or implied. Return them as a comma-separated list.
        
        Description: {description}
        
        Return ONLY the skill list, no explanation.
        """
        
        response = self.call_api(prompt, temperature=0.3, max_tokens=100)
        
        if response:
            skills = [s.strip() for s in response.split(',')]
            return [s for s in skills if s]
        
        return None
    
    def career_advice(self, question: str, context: Dict = None) -> Optional[str]:
        """
        General career advice
        
        Args:
            question: User's question
            context: Additional context
            
        Returns:
            Career advice
        """
        context_str = ""
        if context:
            context_str = f"\n\nContext: {context}"
        
        prompt = f"""
        Answer this career-related question concisely (2-3 sentences):
        
        {question}{context_str}
        """
        
        return self.call_api(prompt, temperature=0.7, max_tokens=300)
    
    def match_explanation(self, career_info: Dict, user_profile: Dict) -> Optional[str]:
        """
        Generate comprehensive explanation for match
        
        Args:
            career_info: Information about the career
            user_profile: User's profile
            
        Returns:
            Match explanation
        """
        prompt = f"""
        Explain why {career_info.get('title', 'this career')} is a strong match 
        for this candidate. Make it specific and encouraging.
        
        Career Highlights:
        - Salary: {career_info.get('salary_range', 'Competitive')}
        - Demand: {career_info.get('demand_score', 'High')}/10
        - Industries: {career_info.get('industries', 'Various')}
        - Match Score: {career_info.get('match_score', 'High')}%
        
        Candidate Profile:
        - Current Skills: {', '.join(user_profile.get('skills', [])) or 'Building foundation'}
        - Experience: {user_profile.get('experience_level', '')}
        - Missing Skills: {', '.join(user_profile.get('missing_skills', [])) or 'None major'}
        
        Keep the response to 150-200 words.
        """
        
        return self.call_api(prompt, temperature=0.7, max_tokens=300)


class MockLLM:
    """
    Mock LLM for testing without API key
    Provides hardcoded but realistic responses
    """
    
    @staticmethod
    def explain_recommendation(career_title: str, match_score: float, 
                              user_skills: List[str], 
                              required_skills: List[str]) -> str:
        """Generate mock explanation"""
        if match_score >= 80:
            confidence = "excellent"
        elif match_score >= 60:
            confidence = "strong"
        else:
            confidence = "developing"
        
        return f"You have a {confidence} match for a {career_title} role with {match_score:.0f}% skill alignment. Your existing skills in {', '.join(user_skills[:2])} provide a solid foundation, and focusing on {', '.join(required_skills[-2:])} will maximize your potential in this field."
    
    @staticmethod
    def generate_roadmap(career_title: str, user_skills: List[str],
                        missing_skills: List[str],
                        experience_level: str) -> str:
        """Generate mock roadmap"""
        roadmap = f"""
3-Month Roadmap to become a {career_title}:

**Month 1: Fundamentals**
- Master core concepts in {missing_skills[0] if missing_skills else 'your field'}
- Complete online courses and certifications
- Set up development environment and tools
- Start first mini-project

**Month 2: Practical Skills**
- Build 2-3 portfolio projects
- Learn best practices and industry standards
- Contribute to open-source projects
- Practice problem-solving and coding

**Month 3: Specialization**
- Develop advanced projects showcasing full stack
- Mock interviews and technical assessments
- Network with professionals in the field
- Polish resume and online presence

**Key Resources:**
- Udemy, Coursera, and YouTube for learning
- GitHub for portfolio
- Online communities and forums
        """
        return roadmap
    
    @staticmethod
    def suggest_projects(career_title: str, user_skills: List[str],
                        experience_level: str) -> str:
        """Generate mock project suggestions"""
        primary_skill = user_skills[0] if user_skills else 'Foundation'
        secondary_skill = user_skills[1] if len(user_skills) > 1 else 'Advanced'
        
        projects = f"""
Project Suggestions for {career_title}:

1. **Beginner Project: Personal Dashboard**
   - Skills: {primary_skill}, UI/UX basics
   - Why: Shows ability to build practical tools
   - Timeline: 1-2 weeks

2. **Intermediate Project: Real-time Data Analysis Tool**
   - Skills: {secondary_skill} analysis, visualization
   - Why: Demonstrates core {career_title} capabilities
   - Timeline: 2-3 weeks

3. **Advanced Project: End-to-End Solution**
   - Skills: Full technical stack
   - Why: Shows professional-level readiness
   - Timeline: 4-6 weeks
        """
        return projects
    
    @staticmethod
    def career_advice(question: str, context: Dict = None) -> str:
        """Provide mock career advice"""
        advice_map = {
            "salary": "Research industry standards for your role and experience level. Don't hesitate to negotiate, and consider total compensation including benefits.",
            "learning": "Focus on consistent practice. Build projects, contribute to open source, and learn by doing rather than just watching tutorials.",
            "next": "Identify one key skill gap and dedicate 2-3 months to mastering it. Build a portfolio project showcasing this new skill.",
            "default": "Focus on continuous learning, build a strong portfolio, network in your field, and don't underestimate the power of consistent practice."
        }
        
        question_lower = question.lower()
        for key, advice in advice_map.items():
            if key in question_lower:
                return advice
        
        return advice_map["default"]


def get_llm_instance(use_mock=False, api_key=None):
    """
    Factory function to get LLM instance
    
    Args:
        use_mock: Use mock LLM instead of real API
        api_key: OpenAI API key
        
    Returns:
        LLM instance
    """
    if use_mock:
        return MockLLM()
    
    return LLMIntegration(api_key=api_key)


if __name__ == "__main__":
    # Test mock LLM
    llm = MockLLM()
    
    print(llm.explain_recommendation(
        "Data Scientist",
        85.0,
        ["Python", "SQL"],
        ["Machine Learning", "Statistics"]
    ))
    
    print("\n" + "="*50 + "\n")
    
    print(llm.generate_roadmap(
        "Data Scientist",
        ["Python"],
        ["Machine Learning", "Statistics"],
        "Fresher"
    ))
