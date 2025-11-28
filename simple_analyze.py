from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("Analyze request received")
        
        # Check if file is present
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file'}), 400
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        print(f"File: {file.filename}")
        print(f"Job description length: {len(job_description)}")
        
        if not job_description:
            return jsonify({'error': 'Job description required'}), 400
        
        # Mock analysis results
        results = {
            'id': 1,
            'ats_score': 75,
            'keyword_score': 80,
            'skills_score': 70,
            'experience_score': 75,
            'education_score': 80,
            'matched_keywords': ['python', 'javascript', 'react'],
            'missing_keywords': ['node', 'aws', 'docker'],
            'missing_skills': ['leadership', 'project management'],
            'verdict': 'Shortlisted'
        }
        
        print("Returning mock results")
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    return jsonify({'token': 'test_token', 'name': data.get('name', 'Test User')}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify({'token': 'test_token', 'name': 'Test User'}), 200

@app.route('/history', methods=['GET'])
def history():
    return jsonify([]), 200

if __name__ == '__main__':
    print("Starting simple analyze server...")
    app.run(debug=True, port=5000)