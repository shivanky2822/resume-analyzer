import json
import os
import hashlib
from datetime import datetime

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

def get_user_by_id(user_id):
    users = load_users()
    for email, user in users.items():
        if user['id'] == user_id:
            return user
    return None

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