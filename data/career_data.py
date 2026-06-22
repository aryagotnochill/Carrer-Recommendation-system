"""
Career Dataset Module
Contains job roles, skills, industry mapping, and salary data
"""

import pandas as pd
import json

def get_career_dataset():
    """
    Generate comprehensive career dataset with job roles and requirements
    """
    careers = [
        {
            "id": 1,
            "title": "Data Analyst",
            "description": "Analyze business data and create insights to drive decision making",
            "required_skills": ["Python", "SQL", "Excel", "Data Visualization", "Statistics"],
            "nice_to_have": ["Tableau", "Power BI", "R", "Machine Learning"],
            "industry": ["Finance", "Healthcare", "Retail", "E-commerce"],
            "salary_min": 50000,
            "salary_max": 85000,
            "career_level": ["Fresher", "Internship", "Experienced"],
            "demand_score": 8.5,
            "growth_trend": "Increasing",
            "description_long": "Data Analysts collect, process, and analyze business data to provide actionable insights. They work with databases, create dashboards, and present findings to stakeholders. This role is essential for data-driven decision making in organizations."
        },
        {
            "id": 2,
            "title": "Machine Learning Engineer",
            "description": "Design and build machine learning models and systems at scale",
            "required_skills": ["Python", "Machine Learning", "Deep Learning", "Statistics", "SQL"],
            "nice_to_have": ["TensorFlow", "PyTorch", "Kubernetes", "AWS", "Computer Vision"],
            "industry": ["Technology", "Finance", "Healthcare", "Autonomous Systems"],
            "salary_min": 80000,
            "salary_max": 150000,
            "career_level": ["Internship", "Experienced"],
            "demand_score": 9.2,
            "growth_trend": "Rapidly Increasing",
            "description_long": "ML Engineers build intelligent systems that learn from data. They use advanced algorithms, manage model deployment, and optimize performance. This is one of the most sought-after roles in tech."
        },
        {
            "id": 3,
            "title": "Software Developer",
            "description": "Design, develop, and maintain software applications",
            "required_skills": ["Java", "Python", "JavaScript", "Problem Solving", "Git"],
            "nice_to_have": ["Databases", "System Design", "Cloud Platforms", "Docker"],
            "industry": ["Technology", "Finance", "E-commerce", "SaaS"],
            "salary_min": 45000,
            "salary_max": 120000,
            "career_level": ["Fresher", "Internship", "Experienced"],
            "demand_score": 9.0,
            "growth_trend": "Stable High",
            "description_long": "Software Developers write, test, and maintain code for applications. They work in teams, follow best practices, and continuously improve software quality. This is a foundational role in the tech industry."
        },
        {
            "id": 4,
            "title": "Data Engineer",
            "description": "Build and maintain data infrastructure and pipelines",
            "required_skills": ["Python", "SQL", "Big Data", "Apache Spark", "Cloud Platforms"],
            "nice_to_have": ["Hadoop", "Kafka", "Data Warehousing", "Airflow", "Scala"],
            "industry": ["Technology", "Finance", "E-commerce", "Social Media"],
            "salary_min": 70000,
            "salary_max": 130000,
            "career_level": ["Internship", "Experienced"],
            "demand_score": 8.8,
            "growth_trend": "Rapidly Increasing",
            "description_long": "Data Engineers design and build systems for collecting, storing, and processing large-scale data. They ensure data quality and accessibility for analysts and data scientists to work with."
        },
        {
            "id": 5,
            "title": "Business Analyst",
            "description": "Bridge business requirements and technical solutions",
            "required_skills": ["Communication", "Excel", "SQL", "Problem Solving", "Analytics"],
            "nice_to_have": ["JIRA", "Tableau", "Business Acumen", "Project Management"],
            "industry": ["Finance", "Consulting", "Healthcare", "E-commerce"],
            "salary_min": 55000,
            "salary_max": 95000,
            "career_level": ["Fresher", "Internship", "Experienced"],
            "demand_score": 7.8,
            "growth_trend": "Stable",
            "description_long": "Business Analysts understand business needs and translate them into technical requirements. They work with stakeholders, document processes, and ensure solutions meet business objectives."
        },
        {
            "id": 6,
            "title": "Frontend Developer",
            "description": "Build user-friendly and responsive web interfaces",
            "required_skills": ["JavaScript", "React", "HTML/CSS", "UI/UX", "Git"],
            "nice_to_have": ["TypeScript", "Vue.js", "Angular", "Web Performance", "Mobile"],
            "industry": ["Technology", "E-commerce", "SaaS", "Media"],
            "salary_min": 45000,
            "salary_max": 110000,
            "career_level": ["Fresher", "Internship", "Experienced"],
            "demand_score": 8.7,
            "growth_trend": "Stable High",
            "description_long": "Frontend Developers create the user interface and experience of web applications. They work with design teams, ensure responsiveness, and optimize performance for end users."
        },
        {
            "id": 7,
            "title": "Backend Developer",
            "description": "Build robust server-side applications and APIs",
            "required_skills": ["Python", "Java", "Node.js", "Databases", "API Design"],
            "nice_to_have": ["Microservices", "Docker", "Kubernetes", "Message Queues", "System Design"],
            "industry": ["Technology", "Finance", "E-commerce", "SaaS"],
            "salary_min": 50000,
            "salary_max": 120000,
            "career_level": ["Fresher", "Internship", "Experienced"],
            "demand_score": 8.9,
            "growth_trend": "Stable High",
            "description_long": "Backend Developers build the server-side logic and databases that power applications. They focus on performance, scalability, and data management."
        },
        {
            "id": 8,
            "title": "DevOps Engineer",
            "description": "Manage infrastructure, deployment, and system operations",
            "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Cloud Platforms"],
            "nice_to_have": ["Terraform", "Ansible", "AWS", "Monitoring", "Scripting"],
            "industry": ["Technology", "Finance", "E-commerce", "SaaS"],
            "salary_min": 70000,
            "salary_max": 130000,
            "career_level": ["Internship", "Experienced"],
            "demand_score": 8.6,
            "growth_trend": "Rapidly Increasing",
            "description_long": "DevOps Engineers bridge development and operations, managing infrastructure and automating deployments. They ensure systems are reliable, scalable, and secure."
        },
        {
            "id": 9,
            "title": "AI/ML Consultant",
            "description": "Advise organizations on AI/ML strategy and implementation",
            "required_skills": ["Machine Learning", "Business Strategy", "Communication", "Python", "Industry Knowledge"],
            "nice_to_have": ["Deep Learning", "NLP", "Computer Vision", "Architecture Design"],
            "industry": ["Consulting", "Technology", "Finance", "Healthcare"],
            "salary_min": 90000,
            "salary_max": 160000,
            "career_level": ["Experienced"],
            "demand_score": 8.4,
            "growth_trend": "Rapidly Increasing",
            "description_long": "AI/ML Consultants help organizations adopt AI technologies. They design solutions, manage implementations, and provide strategic guidance for digital transformation."
        },
        {
            "id": 10,
            "title": "Product Manager",
            "description": "Guide product strategy, roadmap, and development",
            "required_skills": ["Strategy", "Analytics", "Communication", "Leadership", "Market Research"],
            "nice_to_have": ["SQL", "A/B Testing", "User Research", "Technical Background"],
            "industry": ["Technology", "E-commerce", "SaaS", "Finance"],
            "salary_min": 80000,
            "salary_max": 150000,
            "career_level": ["Experienced"],
            "demand_score": 7.9,
            "growth_trend": "Increasing",
            "description_long": "Product Managers define product vision, strategy, and roadmap. They work with engineering, design, and marketing to bring products to market successfully."
        },
        {
            "id": 11,
            "title": "Cloud Architect",
            "description": "Design scalable and secure cloud infrastructure",
            "required_skills": ["Cloud Platforms", "System Design", "Security", "Databases", "Networking"],
            "nice_to_have": ["AWS", "Azure", "Infrastructure as Code", "Containers"],
            "industry": ["Technology", "Finance", "E-commerce", "Enterprise"],
            "salary_min": 85000,
            "salary_max": 160000,
            "career_level": ["Experienced"],
            "demand_score": 8.5,
            "growth_trend": "Rapidly Increasing",
            "description_long": "Cloud Architects design and build cloud infrastructure for organizations. They ensure systems are scalable, secure, and cost-effective."
        },
        {
            "id": 12,
            "title": "Data Scientist",
            "description": "Develop data-driven solutions and predictive models",
            "required_skills": ["Python", "Machine Learning", "Statistics", "Data Analysis", "SQL"],
            "nice_to_have": ["Deep Learning", "Big Data", "Visualization", "Domain Knowledge"],
            "industry": ["Technology", "Finance", "Healthcare", "E-commerce"],
            "salary_min": 75000,
            "salary_max": 140000,
            "career_level": ["Internship", "Experienced"],
            "demand_score": 9.1,
            "growth_trend": "Rapidly Increasing",
            "description_long": "Data Scientists use advanced analytics and machine learning to solve complex business problems. They explore data, build models, and communicate insights."
        }
    ]
    
    return pd.DataFrame(careers)


def get_skills_taxonomy():
    """
    Get a taxonomy of skills grouped by category
    """
    return {
        "Programming Languages": [
            "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", 
            "PHP", "Ruby", "Swift", "Kotlin", "TypeScript"
        ],
        "Web Development": [
            "React", "Angular", "Vue.js", "Node.js", "HTML/CSS", "REST APIs",
            "GraphQL", "Web Sockets", "Progressive Web Apps"
        ],
        "Data & Analytics": [
            "SQL", "Python", "R", "Excel", "Data Visualization", "Statistics",
            "ETL", "Data Warehousing", "Analytics"
        ],
        "Machine Learning": [
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "Scikit-learn", "NLP", "Computer Vision", "Reinforcement Learning",
            "Feature Engineering", "Model Deployment"
        ],
        "Big Data": [
            "Apache Spark", "Hadoop", "Kafka", "Hive", "HBase", "Pig",
            "Storm", "Flink", "Big Data Analytics"
        ],
        "Cloud Platforms": [
            "AWS", "Azure", "Google Cloud", "AWS Lambda", "EC2", "S3",
            "RDS", "DynamoDB", "Cloud Storage"
        ],
        "DevOps & Infrastructure": [
            "Docker", "Kubernetes", "CI/CD", "Jenkins", "Git", "Linux",
            "Terraform", "Ansible", "Monitoring", "Logging"
        ],
        "Databases": [
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra",
            "DynamoDB", "Elasticsearch", "Database Design"
        ],
        "Soft Skills": [
            "Communication", "Leadership", "Problem Solving", "Teamwork",
            "Project Management", "Time Management", "Adaptability", "Creativity"
        ],
        "Business": [
            "Business Analysis", "Market Research", "Strategy", "JIRA",
            "Agile", "Scrum", "Business Acumen", "Stakeholder Management"
        ],
        "UI/UX": [
            "UI Design", "UX Design", "Figma", "Adobe XD", "User Research",
            "Prototyping", "Wireframing"
        ],
        "Advanced Tools": [
            "Tableau", "Power BI", "Looker", "Jupyter", "Git", "JIRA",
            "Confluence", "Docker", "Postman"
        ]
    }


def get_industry_list():
    """
    Get list of industries
    """
    return [
        "Technology",
        "Finance",
        "Healthcare",
        "E-commerce",
        "Consulting",
        "Retail",
        "Manufacturing",
        "Education",
        "Entertainment",
        "SaaS",
        "Telecommunications",
        "Energy",
        "Autonomous Systems",
        "Social Media",
        "Enterprise Software"
    ]


def get_education_options():
    """
    Get education qualification options
    """
    return {
        "High School": ["General"],
        "Diploma": ["Electronics", "Computer Science", "Mechanical", "Civil", "Other"],
        "Bachelor": [
            "Computer Science",
            "Information Technology",
            "Electronics",
            "Electrical",
            "Mechanical",
            "Civil",
            "Mathematics",
            "Physics",
            "Other"
        ],
        "Post Graduation": [
            "Master's in CS",
            "Master's in IT",
            "Master's in Data Science",
            "Master's in Business Administration",
            "Other"
        ],
        "Certifications": [
            "AWS Certified",
            "Azure Certified",
            "Google Cloud Certified",
            "Kubernetes Certified",
            "Other"
        ]
    }


def get_experience_levels():
    """
    Get experience level categories
    """
    return {
        "Fresher": "0-1 years experience, recent graduate",
        "Internship": "0-2 years, still learning, internship background",
        "Experienced": "2+ years, professional work experience"
    }


def get_interests():
    """
    Get common professional interests
    """
    return [
        "Building Products",
        "Data Analysis",
        "Machine Learning",
        "Web Development",
        "Mobile Development",
        "Cloud Computing",
        "Cybersecurity",
        "AI/Automation",
        "Entrepreneurship",
        "Management",
        "Consulting",
        "Research",
        "Teaching",
        "Infrastructure",
        "Optimization"
    ]


# Export function to save/load careers as JSON
def save_careers_to_json(filepath):
    """Save career dataset to JSON file"""
    df = get_career_dataset()
    df.to_json(filepath, orient='records', indent=2)
    print(f"Career data saved to {filepath}")


def load_careers_from_json(filepath):
    """Load career dataset from JSON file"""
    df = pd.read_json(filepath)
    return df


if __name__ == "__main__":
    # Generate and save dataset
    careers_df = get_career_dataset()
    print("Career Dataset:")
    print(careers_df[['title', 'demand_score', 'salary_min', 'salary_max']])
    print(f"\nTotal careers: {len(careers_df)}")
    print(f"\nSkills Taxonomy: {len(get_skills_taxonomy())} categories")
