from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Server is working!'}), 200

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    print(f"Received: {data}")
    return jsonify({'token': 'test_token', 'name': data.get('name', 'Test User')}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    print(f"Received: {data}")
    return jsonify({'token': 'test_token', 'name': 'Test User'}), 200

if __name__ == '__main__':
    print("Starting test server on port 5000...")
    app.run(debug=True, port=5000)