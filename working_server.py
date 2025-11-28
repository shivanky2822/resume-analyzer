from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("=== Analysis Request Received ===")
        
        # Check file
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        print(f"File: {file.filename}")
        print(f"Job description: {job_description[:100]}...")
        
        if not job_description.strip():
            return jsonify({'error': 'Job description is required'}), 400
        
        # Simple text extraction (mock for now)
        resume_text = f"python developer javascript react node.js experience software engineer bachelor degree university worked developed managed"
        
        # Simple analysis
        results = simple_analysis(resume_text, job_description)
        
        print(f"Analysis complete. ATS Score: {results['ats_score']}%")
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def simple_analysis(resume_text, job_description):
    resume_text = resume_text.lower()
    job_description = job_description.lower()
    
    # Extract words
    jd_words = set(re.findall(r'\\b[a-z]{3,}\\b', job_description))
    resume_words = set(re.findall(r'\\b[a-z]{3,}\\b', resume_text))
    
    # Common skills
    skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git']
    
    # Calculate matches
    matched_keywords = list(jd_words & resume_words)[:10]
    missing_keywords = list(jd_words - resume_words)[:10]
    
    jd_skills = [s for s in skills if s in job_description]
    resume_skills = [s for s in skills if s in resume_text]
    missing_skills = list(set(jd_skills) - set(resume_skills))
    
    # Scores
    keyword_score = min(100, int((len(matched_keywords) / max(len(jd_words), 1)) * 100))
    skills_score = min(100, int((len(resume_skills) / max(len(jd_skills), 1)) * 100)) if jd_skills else 70
    experience_score = 80 if any(word in resume_text for word in ['experience', 'worked', 'developed']) else 40
    education_score = 75 if any(word in resume_text for word in ['degree', 'university', 'college']) else 30
    
    ats_score = int((keyword_score * 0.4) + (skills_score * 0.3) + (experience_score * 0.2) + (education_score * 0.1))
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

if __name__ == '__main__':
    print("Starting working server on port 5000...")
    app.run(debug=True, port=5000)