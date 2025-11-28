from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        print(f"Received signup data: {data}")
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            return jsonify({'error': 'All fields required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        users = load_users()
        
        if email in users:
            return jsonify({'error': 'Email already exists'}), 400
        
        user_id = len(users) + 1
        users[email] = {
            'id': user_id,
            'name': name,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        
        save_users(users)
        print(f"User created successfully: {email}")
        
        return jsonify({'token': f'token_{user_id}', 'name': name}), 201
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': 'Signup failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        users = load_users()
        
        if email not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = users[email]
        if user['password'] != hash_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        return jsonify({'token': f'token_{user["id"]}', 'name': user['name']}), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is working!'}), 200

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(debug=True, port=5000)