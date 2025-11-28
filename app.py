from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import pdfplumber
import docx
import re
import os
from datetime import timedelta, datetime
import json
import hashlib

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CORS(app)
jwt = JWTManager(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# File-based storage functions
USERS_FILE = 'users.json'
ANALYSES_FILE = 'analyses.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_analyses():
    if os.path.exists(ANALYSES_FILE):
        with open(ANALYSES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_analyses(analyses):
    with open(ANALYSES_FILE, 'w') as f:
        json.dump(analyses, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password, name):
    users = load_users()
    
    if email in users:
        return None, "Email already exists"
    
    user_id = len(users) + 1
    users[email] = {
        'id': user_id,
        'name': name,
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    return user_id, None

def authenticate_user(email, password):
    users = load_users()
    
    if email not in users:
        return None, "Invalid credentials"
    
    user = users[email]
    if user['password'] != hash_password(password):
        return None, "Invalid credentials"
    
    return user, None

def save_analysis(user_id, filename, job_description, results):
    analyses = load_analyses()
    
    analysis = {
        'id': len(analyses) + 1,
        'user_id': user_id,
        'filename': filename,
        'job_description': job_description,
        'created_at': datetime.now().isoformat(),
        **results
    }
    
    analyses.append(analysis)
    save_analyses(analyses)
    return analysis['id']

def get_user_analyses(user_id):
    analyses = load_analyses()
    return [a for a in analyses if a['user_id'] == user_id]

def get_analysis_by_id(analysis_id, user_id):
    analyses = load_analyses()
    for analysis in analyses:
        if analysis['id'] == analysis_id and analysis['user_id'] == user_id:
            return analysis
    return None

def extract_text(file_path):
    ext = file_path.lower().split('.')[-1]
    text = ""
    
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif ext in ['docx', 'doc']:
        doc = docx.Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
    
    return text.lower()

def analyze_resume(resume_text, job_description):
    resume_text = resume_text.lower()
    job_description = job_description.lower()
    
    jd_words = set(re.findall(r'\b[a-z]{3,}\b', job_description))
    resume_words = set(re.findall(r'\b[a-z]{3,}\b', resume_text))
    
    common_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 
                     'kubernetes', 'git', 'agile', 'scrum', 'leadership', 'communication',
                     'machine learning', 'data analysis', 'project management']
    
    matched_keywords = list(jd_words & resume_words)[:20]
    missing_keywords = list(jd_words - resume_words)[:15]
    
    keyword_score = min(100, int((len(matched_keywords) / max(len(jd_words), 1)) * 100))
    
    jd_skills = [skill for skill in common_skills if skill in job_description]
    resume_skills = [skill for skill in common_skills if skill in resume_text]
    matched_skills = list(set(jd_skills) & set(resume_skills))
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    skills_score = min(100, int((len(matched_skills) / max(len(jd_skills), 1)) * 100)) if jd_skills else 50
    
    exp_keywords = ['years', 'experience', 'worked', 'developed', 'managed', 'led']
    exp_count = sum(1 for word in exp_keywords if word in resume_text)
    experience_score = min(100, exp_count * 15)
    
    edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
    edu_count = sum(1 for word in edu_keywords if word in resume_text)
    education_score = min(100, edu_count * 20)
    
    ats_score = int((keyword_score * 0.4) + (skills_score * 0.3) + 
                    (experience_score * 0.2) + (education_score * 0.1))
    
    verdict = "Shortlisted" if ats_score >= 60 else "Not Shortlisted"
    
    return {
        'ats_score': ats_score,
        'keyword_score': keyword_score,
        'skills_score': skills_score,
        'experience_score': experience_score,
        'education_score': education_score,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords,
        'missing_skills': missing_skills,
        'verdict': verdict
    }

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        print(f"Signup request: {data}")
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            return jsonify({'error': 'All fields required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        user_id, error = create_user(email, password, name)
        
        if error:
            return jsonify({'error': error}), 400
        
        token = create_access_token(identity=user_id)
        print(f"User created successfully: {email}")
        return jsonify({'token': token, 'name': name}), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': 'Signup failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        print(f"Login request: {data}")
        
        email = data.get('email')
        password = data.get('password')
        
        user, error = authenticate_user(email, password)
        
        if error:
            return jsonify({'error': error}), 401
        
        token = create_access_token(identity=user['id'])
        print(f"Login successful: {email}")
        return jsonify({'token': token, 'name': user['name']}), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/analyze', methods=['POST'])
@jwt_required()
def analyze():
    user_id = get_jwt_identity()
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file'}), 400
    
    file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    if not job_description:
        return jsonify({'error': 'Job description required'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{user_id}_{filename}")
    file.save(filepath)
    
    resume_text = extract_text(filepath)
    results = analyze_resume(resume_text, job_description)
    
    analysis_id = save_analysis(user_id, filename, job_description, results)
    
    os.remove(filepath)
    
    return jsonify({'id': analysis_id, **results}), 200

@app.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = get_jwt_identity()
    analyses = get_user_analyses(user_id)
    
    return jsonify([{
        'id': a['id'],
        'filename': a['filename'],
        'ats_score': a['ats_score'],
        'verdict': a['verdict'],
        'created_at': a['created_at']
    } for a in analyses]), 200

@app.route('/analysis/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    user_id = get_jwt_identity()
    analysis = get_analysis_by_id(analysis_id, user_id)
    
    if not analysis:
        return jsonify({'error': 'Analysis not found'}), 404
    
    return jsonify(analysis), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)