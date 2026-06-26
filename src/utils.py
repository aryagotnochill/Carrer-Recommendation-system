"""
Preprocessing and Utilities Module
Handles text cleaning, vectorization, and data preprocessing
"""

import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
from datetime import datetime
import hashlib
import os


class TextPreprocessor:
    """Preprocess and clean text data"""
    
    @staticmethod
    def clean_text(text):
        """
        Clean and normalize text
        """
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def extract_keywords(text, max_keywords=10):
        """Extract keywords from text using simple word frequency"""
        cleaned = TextPreprocessor.clean_text(text)
        words = cleaned.split()
        
        # Filter out short words
        words = [w for w in words if len(w) > 3]
        
        # Get unique words (simplified)
        keywords = list(set(words))[:max_keywords]
        
        return keywords


class SkillMatcher:
    """Match and analyze skills"""
    
    def __init__(self, all_skills_list):
        """
        Initialize with a list of all available skills
        
        Args:
            all_skills_list: List of all valid skills
        """
        self.all_skills = [s.lower() for s in all_skills_list]
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
        
    def extract_skills_from_text(self, text):
        """
        Extract skills mentioned in user text by fuzzy matching
        """
        cleaned = TextPreprocessor.clean_text(text).lower()
        words = cleaned.split()
        
        matched_skills = []
        
        for word in words:
            # Exact match
            if word in self.all_skills:
                matched_skills.append(word)
            # Partial match
            else:
                for skill in self.all_skills:
                    if word in skill or skill in word:
                        if len(word) > 3:  # Avoid short word matches
                            matched_skills.append(skill)
                            break
        
        return list(set(matched_skills))  # Remove duplicates
    
    def calculate_skill_match(self, user_skills, required_skills):
        """
        Calculate skill match percentage
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills
            
        Returns:
            match_percentage: Percentage of skills matched
            extra_skills: Skills user has but not required
            missing_skills: Required skills user doesn't have
        """
        user_skills_lower = [s.lower() for s in user_skills]
        required_skills_lower = [s.lower() for s in required_skills]
        
        matched = len(set(user_skills_lower) & set(required_skills_lower))
        total = len(required_skills_lower)
        
        match_percentage = (matched / total * 100) if total > 0 else 0
        extra_skills = list(set(user_skills_lower) - set(required_skills_lower))
        missing_skills = list(set(required_skills_lower) - set(user_skills_lower))
        
        return {
            'match_percentage': min(100, match_percentage),
            'matched_count': matched,
            'total_required': total,
            'extra_skills': extra_skills,
            'missing_skills': missing_skills
        }


class ContentBasedRecommender:
    """Content-based career recommendation using TF-IDF similarity"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
    def compute_profile_vector(self, user_data):
        """
        Create a user profile vector from their information
        
        Args:
            user_data: Dictionary with keys: skills, education, projects, interests
            
        Returns:
            Combined profile text
        """
        components = []
        
        if 'skills' in user_data and user_data['skills']:
            components.append(" ".join(user_data['skills']))
        
        if 'education' in user_data and user_data['education']:
            components.append(user_data['education'].replace('_', ' '))
        
        if 'projects' in user_data and user_data['projects']:
            components.append(user_data['projects'])
        
        if 'interests' in user_data and user_data['interests']:
            components.append(" ".join(user_data['interests']))
        
        profile_text = " ".join(components)
        return profile_text
    
    def compute_career_vector(self, career_row):
        """
        Create a career vector from job role information
        
        Args:
            career_row: Row from careers dataframe
            
        Returns:
            Combined career description
        """
        components = [
            career_row.get('title', ''),
            career_row.get('description', ''),
            " ".join(career_row.get('required_skills', [])),
            " ".join(career_row.get('nice_to_have', [])),
            " ".join(career_row.get('industry', []))
        ]
        
        career_text = " ".join(str(c) for c in components if c)
        return career_text
    
    def recommend(self, user_data, careers_df, top_n=5):
        """
        Recommend careers based on content similarity
        
        Args:
            user_data: User profile dictionary
            careers_df: DataFrame with career data
            top_n: Number of top recommendations
            
        Returns:
            DataFrame with scores
        """
        user_profile = self.compute_profile_vector(user_data)
        
        career_profiles = [
            self.compute_career_vector(row) for idx, row in careers_df.iterrows()
        ]
        
        # Vectorize
        all_texts = [user_profile] + career_profiles
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity
            similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]
            
            # Add scores to dataframe
            careers_df_copy = careers_df.copy()
            careers_df_copy['content_score'] = similarities
            
            # Sort and return top N
            return careers_df_copy.nlargest(top_n, 'content_score')
        
        except Exception as e:
            print(f"Error in recommendation: {e}")
            # Return top careers by demand if error
            return careers_df.nlargest(top_n, 'demand_score')


class DatabaseManager:
    """Manage SQLite database for user profiles and history"""
    
    def __init__(self, db_path='database/career_app.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skills TEXT,
                education TEXT,
                projects TEXT,
                experience_level TEXT,
                interests TEXT,
                preferred_industry TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Recommendations history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recommended_career TEXT,
                score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            conn.commit()
            conn.close()
            return True, "Registration successful"
        except sqlite3.IntegrityError:
            return False, "Username or email already exists"
        except Exception as e:
            return False, str(e)
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, password_hash FROM users WHERE username = ?',
                (username,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_id, stored_hash = result
                if stored_hash == self.hash_password(password):
                    return True, user_id
            
            return False, None
        except Exception as e:
            return False, str(e)
    
    def save_user_profile(self, user_id, profile_data):
        """Save or update user profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id FROM user_profiles WHERE user_id = ?', (user_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE user_profiles
                    SET skills = ?,
                        education = ?,
                        projects = ?,
                        experience_level = ?,
                        interests = ?,
                        preferred_industry = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (
                    ','.join(profile_data.get('skills', [])),
                    profile_data.get('education', ''),
                    profile_data.get('projects', ''),
                    profile_data.get('experience_level', ''),
                    ','.join(profile_data.get('interests', [])),
                    profile_data.get('preferred_industry', ''),
                    user_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO user_profiles 
                    (user_id, skills, education, projects, experience_level, interests, preferred_industry, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (
                    user_id,
                    ','.join(profile_data.get('skills', [])),
                    profile_data.get('education', ''),
                    profile_data.get('projects', ''),
                    profile_data.get('experience_level', ''),
                    ','.join(profile_data.get('interests', [])),
                    profile_data.get('preferred_industry', '')
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def get_user_profile(self, user_id):
        """Retrieve user profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT skills, education, projects, experience_level, interests, preferred_industry FROM user_profiles WHERE user_id = ?',
                (user_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'skills': result[0].split(',') if result[0] else [],
                    'education': result[1] or '',
                    'projects': result[2] or '',
                    'experience_level': result[3] or '',
                    'interests': result[4].split(',') if result[4] else [],
                    'preferred_industry': result[5] or ''
                }
            
            return None
        except Exception as e:
            print(f"Error retrieving profile: {e}")
            return None
    
    def get_or_create_guest_user(self):
        """Get or create a guest user account for anonymous persistence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM users WHERE username = ?', ('guest',))
            result = cursor.fetchone()
            if result:
                conn.close()
                return result[0]
            password_hash = self.hash_password('guest')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', ('guest', password_hash, 'guest@example.com'))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except Exception as e:
            print(f"Error getting or creating guest user: {e}")
            return None

    def save_recommendation(self, user_id, career_title, score):
        """Save recommendation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recommendations (user_id, recommended_career, score)
                VALUES (?, ?, ?)
            ''', (user_id, career_title, score))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving recommendation: {e}")
            return False
    
    def get_user_recommendations_history(self, user_id, limit=10):
        """Get recommendation history for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT recommended_career, score, timestamp 
                FROM recommendations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return results
        except Exception as e:
            print(f"Error retrieving history: {e}")
            return []


if __name__ == "__main__":
    # Test preprocessing
    text = "I have experience with Python, Machine Learning, and Data Analysis"
    preprocessor = TextPreprocessor()
    print(f"Original: {text}")
    print(f"Cleaned: {preprocessor.clean_text(text)}")
    
    # Test skill matcher
    all_skills = ["Python", "Java", "Machine Learning", "Data Analysis"]
    matcher = SkillMatcher(all_skills)
    print(f"Extracted skills: {matcher.extract_skills_from_text(text)}")
