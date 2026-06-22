# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites
- Python 3.8+ installed
- pip (Python package manager)
- 500MB disk space

### Option 1: Quick Setup (Recommended)

```bash
# 1. Navigate to project directory
cd career-recommendation-system

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

**That's it!** The app opens at `http://localhost:8501`

---

### Option 2: Docker Setup

```bash
# Build Docker image
docker build -t career-system .

# Run container
docker run -p 8501:8501 career-system

# Access at http://localhost:8501
```

---

### Option 3: Cloud Deployment (Streamlit Cloud)

1. Push to GitHub:
```bash
git push origin main
```

2. Go to [Streamlit Cloud](https://share.streamlit.io)

3. Click "New app" → Select GitHub repo and main branch

4. Deploy! Your app gets a public URL

---

## 📖 Usage Guide

### Step 1: Fill Your Profile

**In the sidebar:**
- Click on skill categories to select skills
- Or type skills in free text box
- Select education level and branch
- Choose experience level
- Pick interests (multi-select)
- Describe projects (if any)
- Select preferred industry (optional)

### Step 2: Get Recommendations

Click the **"🎯 Get Recommendations"** button

*Wait 5-10 seconds for analysis*

### Step 3: Explore Results

**Tab 1 - Recommendations:**
- See top 5 careers matched to your profile
- View match scores in gauges
- Click "ℹ️ Details" for more info

**Tab 2 - Skill Gap:**
- Analyze your skill gaps
- See learning time estimates
- Review missing skills

**Tab 3 - Learning Roadmap:**
- AI-generated week-by-week plan
- Tools and projects to learn
- Timeline estimates

**Tab 4 - Career Insights:**
- Market demand comparison
- Salary ranges
- Growth trends

**Tab 5 - Project Suggestions:**
- Portfolio projects to build
- Progressive difficulty
- Timeline for each

**Tab 6 - Summary:**
- Profile overview
- Comparison table
- Export options

---

## 🔧 Configuration

### Use Real OpenAI API (Optional)

1. Get API key from [OpenAI Platform](https://platform.openai.com/api-keys)

2. Create `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```

3. Update `app.py` line ~70:
```python
# From this:
llm = get_llm_instance(use_mock=True)

# To this:
llm = get_llm_instance(use_mock=False)
```

4. Install openai package (already in requirements.txt)

5. Restart app

---

## 📁 Project Structure

```
career-recommendation-system/
├── app.py                      # Main app - RUN THIS
├── requirements.txt            # Dependencies
├── README.md                   # Full documentation
│
├── data/
│   └── career_data.py         # Career dataset & taxonomy
│
├── src/
│   ├── model.py               # ML recommendation engine
│   ├── utils.py               # Utilities & preprocessing
│   └── llm_integration.py      # OpenAI integration
│
├── database/
│   └── career_app.db          # SQLite database (auto-created)
│
└── docs/
    ├── PROBLEM_STATEMENT.md    # Project overview
    ├── SYSTEM_ARCHITECTURE.md  # Technical design
    └── VIVA_QUESTIONS_ANSWERS.md  # Interview prep
```

---

## 🧪 Testing the System

### Test with Sample Data

The app includes sample careers and skills taxonomy. No additional setup needed!

### Test Recommendations

Try different profiles:

**Profile 1: Fresh Python Developer**
- Skills: Python, JavaScript, Git
- Education: Bachelor's in CS
- Experience: Fresher
- Interests: Web Development, Problem Solving

Expected: Software Developer, Frontend Developer recommended

**Profile 2: Data Enthusiast**
- Skills: Python, SQL, Excel, Statistics
- Education: Bachelor's in Math
- Experience: Internship
- Interests: Data Analysis, Machine Learning

Expected: Data Analyst, Data Scientist recommended

**Profile 3: Experienced Full-Stack**
- Skills: Python, Java, JavaScript, SQL, Docker, Kubernetes
- Education: Bachelor's in IT
- Experience: Experienced
- Interests: Cloud Computing, Leadership

Expected: DevOps Engineer, Cloud Architect recommended

---

## 🐛 Troubleshooting

### Issue: Streamlit module not found
```bash
pip install streamlit==1.28.1
```

### Issue: Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

### Issue: Database error
```bash
# Delete and recreate database
rm database/career_app.db
# Restart app - it auto-creates
streamlit run app.py
```

### Issue: LLM API errors
- Make sure you set environment variable correctly
- Check API key is valid
- Ensure internet connection
- App falls back to mock LLM if error

### Issue: Slow recommendations
- First run does TF-IDF training (1-2 seconds)
- Subsequent runs use cache (~100ms)
- LLM calls take 2-5 seconds (normal)

---

## 📊 Example Outputs

### Recommendation Card
```
Data Analyst
Analyze business data and create insights to drive decision making

💰 $50,000 - $85,000 
📈 Demand: 8.5/10 
📊 Increasing

Match Score: 87% ✓
```

### Skill Gap Analysis
```
Match Breakdown:
✅ Matched: 4 skills
❌ Missing: 2 skills  
📌 Extra: 1 skill

Readiness: 80% - Good foundation
Learning Time: 4 weeks
```

### Learning Roadmap (AI-Generated)
```
**Month 1: Fundamentals**
- Master Python advanced concepts
- Complete online statistics course
- Set up Tableau environment
- Build first dashboard

**Month 2: Practical Skills**
- 2-3 real data analysis projects
- Learn data cleaning best practices
- Practice SQL queries
```

---

## 🎯 Next Steps

1. **Explore the UI**: Try different profile combinations
2. **Review the Code**: Check implementation details in `src/`
3. **Read Documentation**: Full docs in `docs/` folder
4. **Customize**: Add your own careers or skills
5. **Deploy**: Push to Streamlit Cloud for sharing
6. **Extend**: Add your own features (resume parser, etc.)

---

## 📞 Support & Resources

**Documentation:**
- [Full README](README.md)
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
- [Viva Q&A](docs/VIVA_QUESTIONS_ANSWERS.md)

**External Resources:**
- [Streamlit Docs](https://docs.streamlit.io)
- [Scikit-learn Documentation](https://scikit-learn.org)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [SQLite Reference](https://www.sqlite.org/docs.html)

---

## 🎉 Have Fun!

You now have a fully functional career recommendation system. Experiment, learn, and enjoy building with AI and ML!

**Questions?** Check the docs or viva questions section for detailed explanations.

Happy exploring! 🚀
