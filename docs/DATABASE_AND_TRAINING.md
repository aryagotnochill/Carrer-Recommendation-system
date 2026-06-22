# Database & Training Data Architecture

## 📍 Database Location

```
project_root/
├── database/
│   └── career_app.db  ← SQLite Database (Auto-created on first run)
│
└── data/
    ├── career_data.py  ← Training Data Source (12 careers)
    └── __init__.py
```

### Database Path
```python
# Location: database/career_app.db
# Type: SQLite 3
# Auto-created: Yes (on first app run)
# Size: ~2-5 MB (grows with users)
```

---

## 🗂️ Database Schema

### 3 Main Tables:

#### 1. **users** Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```
**Purpose**: Store user authentication
**Sample Data**: User credentials (sample users can be created)

#### 2. **user_profiles** Table
```sql
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skills TEXT,                    -- CSV format
    education TEXT,
    projects TEXT,
    experience_level TEXT,
    interests TEXT,                 -- CSV format
    preferred_industry TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```
**Purpose**: Store user input data
**Sample Data**: User's skills, education, projects, etc.

#### 3. **recommendations** Table
```sql
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommended_career TEXT,
    score REAL,
    timestamp TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
```
**Purpose**: Store recommendation history
**Sample Data**: Career recommendations and scores for users

---

## 🎓 Training Data Source

### Location: **`data/career_data.py`**

### 12 Careers In-Memory Dataset

The careers are **hardcoded** in Python (no external database):

```python
[
    1. Data Analyst
    2. Machine Learning Engineer
    3. Software Developer
    4. Data Engineer
    5. Business Analyst
    6. Frontend Developer
    7. Backend Developer
    8. DevOps Engineer
    9. AI/ML Consultant
    10. Product Manager
    11. Cloud Architect
    12. Data Scientist
]
```

### Career Data Structure

```python
{
    "id": 1,
    "title": "Data Analyst",
    "description": "...",
    "required_skills": ["Python", "SQL", "Excel", ...],
    "nice_to_have": ["Tableau", "Power BI", ...],
    "industry": ["Finance", "Healthcare", ...],
    "salary_min": 50000,
    "salary_max": 85000,
    "career_level": ["Fresher", "Internship", "Experienced"],
    "demand_score": 8.5,          # 0-10 scale
    "growth_trend": "Increasing",
    "description_long": "..."
}
```

### Skills Taxonomy (100+ Skills)

```python
{
    "Programming Languages": ["Python", "Java", "JS", ...],
    "Web Development": ["React", "Vue", "Angular", ...],
    "Data & Analytics": ["SQL", "Excel", "Tableau", ...],
    "Machine Learning": ["TensorFlow", "Scikit-learn", ...],
    "Big Data": ["Apache Spark", "Hadoop", ...],
    "Cloud Platforms": ["AWS", "Azure", "GCP", ...],
    "DevOps & Infrastructure": ["Docker", "Kubernetes", ...],
    "Databases": ["MySQL", "MongoDB", "PostgreSQL", ...],
    "Soft Skills": ["Communication", "Leadership", ...],
    "Business": ["Project Management", "Strategy", ...],
    "UI/UX": ["Figma", "Adobe XD", ...]
}
```

---

## 🔄 Data Flow Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    STREAMLIT APP (UI)                          │
│              localhost:8502                                    │
└────────────────────┬───────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   ┌─────────────┐        ┌──────────────┐
   │  User Input │        │ Display      │
   │  - Skills   │        │ - Career     │
   │  - Education│        │ - Graphs     │
   │  - Projects │        │ - Insights   │
   └────────┬────┘        └──────────────┘
            │
            ▼
   ┌─────────────────────────────────────┐
   │  Recommendation Engines             │
   │  ┌─────────────────────────────┐    │
   │  │ HYBRID ENGINE               │    │
   │  │ - TF-IDF Scoring            │    │ ← Initialized once in memory
   │  │ - Skill Matching            │    │
   │  │ - Experience Matching       │    │
   │  │ - Demand Scoring            │    │
   │  └─────────────────────────────┘    │
   │  ┌─────────────────────────────┐    │
   │  │ RANDOM FOREST ENGINE        │    │
   │  │ - 100 Decision Trees        │    │ ← Trained on 12 careers
   │  │ - Feature Importance        │    │
   │  │ - Success Probability       │    │
   │  └─────────────────────────────┘    │
   │  ┌─────────────────────────────┐    │
   │  │ LLM INTEGRATION             │    │
   │  │ - Explanations              │    │
   │  │ - Roadmaps                  │    │
   │  │ - Project Ideas             │    │
   │  └─────────────────────────────┘    │
   └──────────┬──────────────────────────┘
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
 ┌─────────────┐  ┌──────────────────┐
 │  DATABASES  │  │ TRAINING DATA    │
 │             │  │                  │
 │ ┌─────────┐ │  │ ┌──────────────┐ │
 │ │ users   │ │  │ │ 12 Careers   │ │
 │ ├─────────┤ │  │ ├──────────────┤ │
 │ │ profiles│ │  │ │ 100+ Skills  │ │
 │ ├─────────┤ │  │ ├──────────────┤ │
 │ │ recomds │ │  │ │ Industries   │ │
 │ └─────────┘ │  │ └──────────────┘ │
 │             │  │                  │
 │ SQLite      │  │ In Memory        │
 │ 3-5 MB      │  │ (Python Lists)   │
 └─────────────┘  └──────────────────┘
```

---

## 📊 Training Data Details

### Where Data Comes From:

```python
# File: data/career_data.py

def get_career_dataset():
    """Returns 12 careers as DataFrame"""
    careers = [
        {career1_dict},
        {career2_dict},
        ...
        {career12_dict}
    ]
    return pd.DataFrame(careers)

def get_skills_taxonomy():
    """Returns 100+ skills organized in 11 categories"""
    return {
        "Programming Languages": [...],
        "Web Development": [...],
        ...
    }
```

### How It's Used:

```
Step 1: App Loads
       └─> Calls get_career_dataset()
           └─> Returns 12 careers as Pandas DataFrame
               
Step 2: Models Initialize
       └─> Passes careers_df to:
           ├─> CareerRecommendationEngine (Hybrid)
           ├─> RandomForestCareerRecommender (RF model)
           └─> LLMIntegration (for explanations)

Step 3: Models Train (In Memory)
       ├─> Hybrid: Builds TF-IDF vectorizer on 12 careers
       ├─> Random Forest: Trains 100 trees on career features
       └─> All happens in RAM in ~100ms

Step 4: User Makes Request
       └─> Models use trained weights to score 12 careers
           └─> Returns top 5 matching careers
```

---

## 💾 Database Operations

### When Database is Used:

1. **User Registration** → Stores in `users` table
2. **User Profile Save** → Stores in `user_profiles` table
3. **Recommendation History** → Stores in `recommendations` table
4. **User Login** → Reads from `users` table

### When Database is NOT Used:

- ❌ Model training (uses in-memory data only)
- ❌ Recommendation generation (uses in-memory models)
- ❌ LLM callbacks (uses OpenAI API)
- ❌ Feature engineering (uses user input)

---

## 🔍 Training Workflow

### ML Model Training:

```python
# In app.py initialization

@st.cache_resource
def initialize_engine(careers_df, all_skills):
    """Train model once and cache"""
    return CareerRecommendationEngine(careers_df, all_skills)

# STEP BY STEP:

1. Load 12 careers from data/career_data.py
   ↓
2. Extract all skills (100+) from careers
   ↓
3. Create TF-IDF vectorizer
   ├─> Fit on career descriptions
   ├─> Fit on skill combinations
   └─> Create similarity matrix (12x12)
   ↓
4. Train Random Forest
   ├─> 100 decision trees
   ├─> Learn career feature patterns
   └─> Store feature importances
   ↓
5. Cache models (@st.cache_resource)
   └─> Reused for all subsequent requests
```

---

## 🎯 Complete Data Sources Map

| Component | Source | Type | Size |
|-----------|--------|------|------|
| **Careers** | `data/career_data.py` | Hardcoded | 12 roles |
| **Skills** | `data/career_data.py` | Hardcoded | 100+ skills |
| **Industries** | `data/career_data.py` | Hardcoded | 15 industries |
| **User Data** | `database/career_app.db` | SQLite | Dynamic |
| **Models** | In-Memory Cache | Trained | RAM only |
| **LLM Help** | OpenAI API | External | Optional |

---

## 🚀 Quick Summary

### Question 1: Where is the database?
```
📍 Location: database/career_app.db
📝 Type: SQLite 3
👤 Contains: User profiles, credentials, recommendation history
📊 Size: 3-5 MB (grows with users)
🔄 Auto-created: Yes (first run)
```

### Question 2: Where is it being trained?
```
🎓 Training Data: data/career_data.py
🔢 Sample Size: 12 careers (+ 100+ skills)
⚙️ Training Location: In-Memory (Python lists)
📈 Model Type: Hybrid (TF-IDF + Random Forest)
⏱️ Training Time: ~100ms (on app startup)
💾 Storage: Cached in RAM (automatically)
```

---

## 📁 File Structure Explanation

```
career-recommendation-system/
│
├── 📊 TRAINING DATA (No DB)
│   └── data/career_data.py
│       ├── 12 careers (hardcoded)
│       ├── 100+ skills (taxonomy)
│       └── Returns as DataFrame
│
├── 🤖 MODELS (In Memory)
│   ├── src/model.py (Hybrid Engine - TF-IDF)
│   ├── src/random_forest_model.py (RF - 100 trees)
│   └── src/llm_integration.py (OpenAI)
│
├── 💾 USER DATABASE (SQLite)
│   └── database/career_app.db
│       ├── users (authentication)
│       ├── user_profiles (input data)
│       └── recommendations (history)
│
└── 🎨 UI & DISPLAY
    └── app.py (Streamlit)
```

---

## 🔗 Data Loading Flow

```
App Start
   ↓
1. Load careers from data/career_data.py
   └─> careers_df = get_career_dataset()
   └─> Returns 12 careers as DataFrame
   ↓
2. Load skills from data/career_data.py
   └─> skills_taxonomy = get_skills_taxonomy()
   └─> Returns 100+ skills organized
   ↓
3. Initialize careers_df in CareerRecommendationEngine
   └─> Trains TF-IDF on descriptions
   └─> Caches in memory
   ↓
4. Initialize Random Forest
   └─> Trains on all 12 careers
   └─> Caches feature weights
   ↓
5. Initialize Database
   └─> database/career_app.db
   └─> Creates tables if not exists
   ↓
6. App Ready!
   └─> User can input profile
   └─> Models recommend careers
   └─> Results saved to database
```

---

## ✅ Answer Summary

**Q: Where is the database?**
- **A:** `database/career_app.db` (SQLite, auto-created)

**Q: From where is it being trained?**
- **A:** `data/career_data.py` (12 careers + 100+ skills, hardcoded in Python)

**Additional Info:**
- Models trained: In-memory (not persisted)
- Training time: ~100ms on startup
- Training data size: 12 careers
- Training happens: During app initialization
- Database contains: User data only (not training data)

---

**Status**: ✅ All data sources documented
**Database**: SQLite at `database/career_app.db`
**Training Data**: Python lists in `data/career_data.py`
