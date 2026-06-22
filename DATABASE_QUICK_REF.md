# Database & Training Quick Reference

## 🎯 Two Key Locations

### 1️⃣ DATABASE (User Data)
```
📁 Location: /database/career_app.db
📊 Type: SQLite 3
📝 Contains: 
   - User accounts (username, password)
   - User profiles (skills, education, projects)
   - Recommendation history
💾 Size: 3-5 MB
🔄 Auto-created: Yes (first run)
```

### 2️⃣ TRAINING DATA (Career Data)
```
📁 Location: /data/career_data.py
📝 Format: Python hardcoded lists
🎯 Contains:
   - 12 Career roles
   - 100+ Skills (11 categories)
   - Industry mappings
   - Salary ranges
⚙️ Size: In-memory only (RAM)
🔄 Auto-loaded: Yes (app startup)
```

---

## 📊 What's in Each?

### Career_app.db (SQLite Database)

**Table 1: users**
```
┌─────────────────────────────────────┐
│ users                               │
├─────────────────────────────────────┤
│ id          (Primary Key)           │
│ username    (String, UNIQUE)        │
│ password_hash (SHA-256)             │
│ email       (String, UNIQUE)        │
│ created_at  (Timestamp)             │
│ last_login  (Timestamp)             │
└─────────────────────────────────────┘
```

**Table 2: user_profiles**
```
┌──────────────────────────────────────────┐
│ user_profiles                            │
├──────────────────────────────────────────┤
│ id                  (Primary Key)        │
│ user_id             (Foreign Key)        │
│ skills              (CSV Text)           │
│ education           (String)             │
│ projects            (Text)               │
│ experience_level    (String)             │
│ interests           (CSV Text)           │
│ preferred_industry  (String)             │
│ created_at          (Timestamp)          │
│ updated_at          (Timestamp)          │
└──────────────────────────────────────────┘
```

**Table 3: recommendations**
```
┌─────────────────────────────────────┐
│ recommendations                     │
├─────────────────────────────────────┤
│ id                  (Primary Key)   │
│ user_id             (Foreign Key)   │
│ recommended_career  (String)        │
│ score               (Float: 0-100)  │
│ timestamp           (Timestamp)     │
└─────────────────────────────────────┘
```

### career_data.py (Training Data)

**12 Careers Available:**

| # | Career | Demand | Salary Range |
|---|--------|--------|--------------|
| 1 | Data Analyst | 8.5/10 | $50K-$85K |
| 2 | ML Engineer | 9.2/10 | $80K-$150K |
| 3 | Software Developer | 9.0/10 | $45K-$120K |
| 4 | Data Engineer | 8.8/10 | $75K-$140K |
| 5 | Business Analyst | 7.5/10 | $55K-$95K |
| 6 | Frontend Developer | 8.7/10 | $50K-$110K |
| 7 | Backend Developer | 8.9/10 | $60K-$130K |
| 8 | DevOps Engineer | 8.3/10 | $70K-$130K |
| 9 | AI/ML Consultant | 8.9/10 | $90K-$160K |
| 10 | Product Manager | 7.8/10 | $80K-$140K |
| 11 | Cloud Architect | 8.6/10 | $100K-$180K |
| 12 | Data Scientist | 9.0/10 | $85K-$160K |

**Skills Categories (11 Total, 100+ Skills):**
- Programming Languages (15 skills)
- Web Development (12 skills)
- Data & Analytics (18 skills)
- Machine Learning (14 skills)
- Big Data (10 skills)
- Cloud Platforms (12 skills)
- DevOps & Infrastructure (10 skills)
- Databases (12 skills)
- Soft Skills (8 skills)
- Business (6 skills)
- UI/UX (6 skills)

---

## 🔄 Data Flow During App Runtime

### Step 1: App Starts
```
streamlit run app.py
    ↓
1. Import data/career_data.py
   └─> Load 12 careers into DataFrame
   └─> Load 100+ skills into dict
       
2. Initialize models (cached in RAM)
   ├─> CareerRecommendationEngine
   │   └─> Trains TF-IDF on careers (~50ms)
   │
   ├─> RandomForestCareerRecommender
   │   └─> Trains 100 trees (~50ms)
   │
   └─> LLMIntegration
       └─> Ready for API calls
       
3. Initialize database/career_app.db
   └─> Creates 3 tables if not exists
   └─> Ready to store user data
```

### Step 2: User Interacts
```
User enters skills/education
    ↓
app.py receives input
    ↓
Models make predictions (in-memory)
├─> Hybrid: TF-IDF scores + Skill matching
├─> Random Forest: Feature-based scoring
└─> LLM: Generates explanations
    ↓
Results displayed in UI
    ↓
Option: Save to database
└─> INSERT into recommendations table
```

---

## 💾 Database File Location

### Absolute Path
```
Windows:  D:\projects\final\career-recommendation-system\database\career_app.db
Linux:    /path/to/project/database/career_app.db
Mac:      /Users/username/project/database/career_app.db
```

### Relative Path (from app.py)
```
./database/career_app.db
```

### How to Find It
```bash
# In project root directory
ls -la database/

# Output:
# career_app.db  (file size will grow)
```

### To Delete & Reset
```bash
# Delete database to reset (will lose all user data)
rm database/career_app.db

# App will auto-create new database on next run
python -m streamlit run app.py
```

---

## 🔍 Where Models are Trained

### Training Source: career_data.py

```python
# File: data/career_data.py

def get_career_dataset():
    """Training data for models"""
    careers = [
        {
            "id": 1,
            "title": "Data Analyst",
            "required_skills": ["Python", "SQL", "Excel", ...],
            "demand_score": 8.5,
            "salary_min": 50000,
            "salary_max": 85000,
            ...
        },
        # ... 11 more careers
    ]
    return pd.DataFrame(careers)

def get_skills_taxonomy():
    """Skills for skill matching"""
    return {
        "Programming Languages": ["Python", "Java", ...],
        "Web Development": ["React", "Vue", ...],
        # ... 9 more categories
    }
```

### Training Process

```
1. Load data/career_data.py
2. Extract 12 careers as DataFrame
3. Initialize CareerRecommendationEngine
   └─> TF-IDF vectorizer.fit(career_descriptions)
   └─> Creates similarity matrix (12x12)
   ↓
4. Initialize RandomForestCareerRecommender
   └─> RF classifier.fit(career_features, career_id)
   └─> RF regressor.fit(career_features, demand_score)
   ↓
5. Models cached in memory (@st.cache_resource)
   └─> Reused for all requests
   └─> Never reloaded unless settings change
```

---

## 📊 Memory Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                        APP MEMORY (RAM)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐      ┌──────────────────────────────┐    │
│  │  TRAINING DATA   │      │   MODELS (CACHED)            │    │
│  │  (In-Memory)     │      │                              │    │
│  ├──────────────────┤      ├──────────────────────────────┤    │
│  │ 12 careers       │ ───→ │ TF-IDF Vectorizer            │    │
│  │ (DataFrame)      │      │ - Vocabulary (1000+ terms)   │    │
│  │ ~500 KB          │      │ - Career vectors (12x1000)   │    │
│  │                  │      │ - Similarity matrix (12x12)  │    │
│  ├──────────────────┤      ├──────────────────────────────┤    │
│  │ 100+ skills      │ ───→ │ Random Forest (100 trees)    │    │
│  │ (Dict)           │      │ - Feature importances        │    │
│  │ ~50 KB           │      │ - Decision nodes (~1000s)    │    │
│  │                  │      │ - Classifiers & regressors   │    │
│  │                  │      ├──────────────────────────────┤    │
│  │                  │      │ LLM Integration              │    │
│  │                  │      │ - OpenAI client ready        │    │
│  └──────────────────┘      │ - Mock LLM loaded            │    │
│                            └──────────────────────────────┘    │
│                                    ↓                           │
│                            ┌─────────────────┐                 │
│                            │ Ready to use    │                 │
│                            │ ~50-100 MB RAM  │                 │
│                            └─────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 File Organization

```
career-recommendation-system/
│
├── data/
│   ├── career_data.py          ← TRAINING DATA SOURCE
│   │   ├── get_career_dataset()      Returns 12 careers
│   │   ├── get_skills_taxonomy()     Returns 100+ skills
│   │   └── Other getters...
│   └── __init__.py
│
├── database/
│   └── career_app.db           ← USER DATABASE
│       ├── users table              User accounts
│       ├── user_profiles table      User input data
│       └── recommendations table    Career history
│
├── src/
│   ├── model.py                ← HYBRID MODEL (trained on 12 careers)
│   ├── random_forest_model.py  ← RF MODEL (trained on 12 careers)
│   ├── llm_integration.py      ← LLM wrapper
│   └── utils.py                ← Database manager
│
└── app.py
    ├── Loads data/career_data.py
    ├── Trains models
    ├── Initializes database/career_app.db
    └── Runs Streamlit UI
```

---

## ⚡ Quick Facts

| Question | Answer |
|----------|--------|
| **Database file location?** | `database/career_app.db` |
| **Database type?** | SQLite 3 |
| **Training data location?** | `data/career_data.py` |
| **Number of careers?** | 12 |
| **Number of skills?** | 100+ |
| **Models trained on?** | 12 careers (in-memory) |
| **Model training time?** | ~100ms |
| **Database auto-creation?** | Yes (first run) |
| **Training data in database?** | No (hardcoded in Python) |
| **User data in database?** | Yes (SQLite tables) |
| **Models persist to disk?** | No (RAM only, cached) |

---

## 🎓 Summary

### Database (`career_app.db`)
- ✅ Stores: User credentials, profiles, recommendation history
- ✅ Location: `/database/career_app.db`
- ✅ Type: SQLite 3
- ✅ Auto-created: Yes
- ❌ Contains training data: No

### Training Data (`career_data.py`)
- ✅ Source: `/data/career_data.py`
- ✅ Format: Python hardcoded lists
- ✅ 12 Careers
- ✅ 100+ Skills
- ✅ Loaded into RAM on app start
- ✅ Used by all models

### Models
- ✅ Training source: `data/career_data.py`
- ✅ Training location: In-memory (RAM)
- ✅ Training time: ~100ms
- ✅ Cached: Yes (reused for all requests)
- ✅ Persisted: No (only in RAM)

---

**Status**: ✅ Fully documented and explained
**Last Updated**: April 11, 2026
