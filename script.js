const API_BASE = 'http://localhost:5000';
let currentUser = null;
let currentAnalysis = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupEventListeners();
});

function setupEventListeners() {
    // Auth forms
    document.getElementById('loginFormElement').addEventListener('submit', handleLogin);
    document.getElementById('signupFormElement').addEventListener('submit', handleSignup);
    
    // Close modal when clicking outside
    document.getElementById('authModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeAuthModal();
        }
    });
    
    // File upload - only setup if elements exist
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeFile');
    
    if (uploadArea && fileInput) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleDrop);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        
        fileInput.addEventListener('change', handleFileSelect);
    }
}

// Authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    const name = localStorage.getItem('userName');
    
    if (token && name) {
        currentUser = { token, name };
        document.getElementById('userName').textContent = name;
        document.getElementById('userNameAnalyzer').textContent = name;
        showDashboard();
        loadHistory();
    } else {
        showLanding();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('userName', data.name);
            currentUser = { token: data.token, name: data.name };
            document.getElementById('userName').textContent = data.name;
            document.getElementById('userNameAnalyzer').textContent = data.name;
            closeAuthModal();
            showDashboard();
            loadHistory();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Login failed. Please try again.');
    }
}

async function handleSignup(e) {
    e.preventDefault();
    
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    console.log('Signup attempt:', { name, email, password: '***' });
    
    if (password.length < 6) {
        alert('Password must be at least 6 characters');
        return;
    }
    
    try {
        console.log('Sending signup request to:', `${API_BASE}/signup`);
        
        const response = await fetch(`${API_BASE}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        console.log('Signup response status:', response.status);
        
        const data = await response.json();
        console.log('Signup response data:', data);
        
        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('userName', data.name);
            currentUser = { token: data.token, name: data.name };
            document.getElementById('userName').textContent = data.name;
            document.getElementById('userNameAnalyzer').textContent = data.name;
            closeAuthModal();
            showDashboard();
            loadHistory();
        } else {
            alert(data.error || 'Signup failed');
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('Signup failed. Please check console for details.');
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    currentUser = null;
    showLanding();
}

// Navigation
function showLanding() {
    hideAllPages();
    document.getElementById('landingPage').classList.add('active');
}

function showDashboard() {
    hideAllPages();
    document.getElementById('dashboardPage').classList.add('active');
}

function showAnalyzer() {
    hideAllPages();
    document.getElementById('analyzerPage').classList.add('active');
    document.getElementById('resultsSection').style.display = 'none';
}

function hideAllPages() {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
}

// Modal functions
function toggleAuthModal(type) {
    const modal = document.getElementById('authModal');
    modal.classList.add('active');
    switchAuthForm(type);
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.remove('active');
}

function switchAuthForm(type) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (type === 'login') {
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
    } else {
        signupForm.classList.add('active');
        loginForm.classList.remove('active');
    }
}

// File handling
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        document.getElementById('resumeFile').files = files;
        updateUploadArea(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        updateUploadArea(file);
    }
}

function updateUploadArea(file) {
    const uploadArea = document.getElementById('uploadArea');
    uploadArea.innerHTML = `
        <div class="upload-icon">✓</div>
        <p><strong>${file.name}</strong></p>
        <p class="upload-hint">File selected successfully</p>
    `;
}

// Analysis
async function analyzeResume() {
    const fileInput = document.getElementById('resumeFile');
    const jobDescription = document.getElementById('jobDescription').value;
    
    console.log('Starting analysis...');
    console.log('File selected:', fileInput.files[0]);
    console.log('Job description:', jobDescription);
    
    if (!fileInput.files[0]) {
        alert('Please select a resume file');
        return;
    }
    
    if (!jobDescription.trim()) {
        alert('Please enter a job description');
        return;
    }
    
    if (!currentUser || !currentUser.token) {
        alert('Please login first');
        return;
    }
    
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);
    formData.append('job_description', jobDescription);
    
    showLoading();
    
    try {
        console.log('Sending analysis request...');
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentUser.token}`
            },
            body: formData
        });
        
        console.log('Analysis response status:', response.status);
        const data = await response.json();
        console.log('Analysis response data:', data);
        
        if (response.ok) {
            currentAnalysis = data;
            displayResults(data);
            loadHistory(); // Refresh history
        } else {
            alert(data.error || 'Analysis failed');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Analysis failed. Please check console for details.');
    } finally {
        hideLoading();
    }
}

function displayResults(data) {
    document.getElementById('resultsSection').style.display = 'block';
    
    // Main score
    const mainScore = document.getElementById('mainScore');
    const mainScoreCircle = document.getElementById('mainScoreCircle');
    const verdict = document.getElementById('verdict');
    
    mainScore.textContent = data.ats_score;
    verdict.textContent = data.verdict;
    verdict.style.color = data.verdict === 'Shortlisted' ? '#10b981' : '#ef4444';
    
    // Animate score circle
    const percentage = data.ats_score;
    mainScoreCircle.style.background = `conic-gradient(#2E67F8 ${percentage}%, rgba(255, 255, 255, 0.2) 0)`;
    
    // Score breakdown
    animateScoreBar('keywordBar', 'keywordScore', data.keyword_score);
    animateScoreBar('skillsBar', 'skillsScore', data.skills_score);
    animateScoreBar('experienceBar', 'experienceScore', data.experience_score);
    animateScoreBar('educationBar', 'educationScore', data.education_score);
    
    // Keywords and skills
    displayKeywords('matchedKeywords', data.matched_keywords);
    displayKeywords('missingKeywords', data.missing_keywords);
    displayKeywords('missingSkills', data.missing_skills);
}

function animateScoreBar(barId, scoreId, score) {
    const bar = document.getElementById(barId);
    const scoreElement = document.getElementById(scoreId);
    
    setTimeout(() => {
        bar.style.width = `${score}%`;
        scoreElement.textContent = `${score}%`;
    }, 500);
}

function displayKeywords(containerId, keywords) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    keywords.forEach(keyword => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        container.appendChild(tag);
    });
    
    if (keywords.length === 0) {
        container.innerHTML = '<span style="color: rgba(255, 255, 255, 0.6);">None found</span>';
    }
}

// History
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history`, {
            headers: {
                'Authorization': `Bearer ${currentUser.token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayHistory(data);
            updateStats(data);
        }
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function displayHistory(analyses) {
    const historyList = document.getElementById('historyList');
    
    if (analyses.length === 0) {
        historyList.innerHTML = `
            <div class="empty-state">
                <p>No analyses yet. Start by analyzing your first resume!</p>
            </div>
        `;
        return;
    }
    
    historyList.innerHTML = analyses.map(analysis => `
        <div class="history-item">
            <div>
                <strong>${analysis.filename}</strong>
                <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
                    ${new Date(analysis.created_at).toLocaleDateString()}
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.5rem; font-weight: bold; color: ${analysis.verdict === 'Shortlisted' ? '#10b981' : '#ef4444'};">
                    ${analysis.ats_score}%
                </div>
                <div style="color: ${analysis.verdict === 'Shortlisted' ? '#10b981' : '#ef4444'};">
                    ${analysis.verdict}
                </div>
            </div>
        </div>
    `).join('');
}

function updateStats(analyses) {
    const total = analyses.length;
    const avgScore = total > 0 ? Math.round(analyses.reduce((sum, a) => sum + a.ats_score, 0) / total) : 0;
    const shortlisted = analyses.filter(a => a.verdict === 'Shortlisted').length;
    
    document.getElementById('totalAnalyses').textContent = total;
    document.getElementById('avgScore').textContent = `${avgScore}%`;
    document.getElementById('shortlisted').textContent = shortlisted;
}

// Utilities
function showLoading() {
    document.getElementById('loading').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('active');
}

function downloadReport() {
    if (!currentAnalysis) {
        alert('No analysis data available');
        return;
    }
    
    // Create a simple text report
    const report = `
ATS RESUME ANALYSIS REPORT
========================

Overall ATS Score: ${currentAnalysis.ats_score}%
Verdict: ${currentAnalysis.verdict}

SCORE BREAKDOWN:
- Keywords: ${currentAnalysis.keyword_score}%
- Skills: ${currentAnalysis.skills_score}%
- Experience: ${currentAnalysis.experience_score}%
- Education: ${currentAnalysis.education_score}%

MATCHED KEYWORDS:
${currentAnalysis.matched_keywords.join(', ') || 'None'}

MISSING KEYWORDS:
${currentAnalysis.missing_keywords.join(', ') || 'None'}

MISSING SKILLS:
${currentAnalysis.missing_skills.join(', ') || 'None'}

RECOMMENDATIONS:
- Include more relevant keywords from the job description
- Highlight matching skills prominently
- Quantify your achievements with numbers
- Use action verbs to describe your experience
    `;
    
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ats-analysis-report.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}