from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devops-trivia-secret-key'
CORS(app)

def get_db():
    return sqlite3.connect('trivia.db')

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                  password_hash TEXT, score INTEGER DEFAULT 0, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions
                 (id INTEGER PRIMARY KEY, question_text TEXT, 
                  options TEXT, correct_answer INTEGER)''')
    
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        questions = [
            (1, "What does DevOps combine?", '["Development and Operations","Design and Operations","Development and Security","Data and Operations"]', 0),
            (2, "What is CI in DevOps?", '["Continuous Integration","Code Integration","Continuous Improvement","Computer Integration"]', 0),
            (3, "What does CD stand for?", '["Continuous Delivery","Code Deployment","Computer Design","Continuous Data"]', 0),
            (4, "Which tool is used for version control?", '["Git","Docker","Jenkins","Kubernetes"]', 0),
            (5, "What is Docker used for?", '["Containerization","Version control","Monitoring","Testing"]', 0),
        ]
        for q in questions:
            c.execute("INSERT INTO questions (id, question_text, options, correct_answer) VALUES (?, ?, ?, ?)", q)
    
    conn.commit()
    conn.close()

init_db()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['username']
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, score) VALUES (?, ?, ?)", 
                  (username, hashed.decode('utf-8'), 0))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created successfully'}), 201
    except:
        return jsonify({'error': 'Username already exists'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
        token = jwt.encode({'username': username, 'exp': datetime.utcnow() + timedelta(hours=24)}, 
                          app.config['SECRET_KEY'])
        return jsonify({'token': token, 'username': username, 'score': user[3]}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10")
    leaders = [{'username': row[0], 'score': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(leaders), 200

@app.route('/api/questions', methods=['GET'])
@token_required
def get_questions(current_user):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, question_text, options FROM questions ORDER BY RANDOM() LIMIT 5")
    questions = []
    for row in c.fetchall():
        questions.append({
            'id': row[0],
            'question_text': row[1],
            'options': eval(row[2])
        })
    conn.close()
    return jsonify(questions), 200

@app.route('/api/submit-answer', methods=['POST'])
@token_required
def submit_answer(current_user):
    data = request.json
    question_id = data.get('question_id')
    user_answer = data.get('answer')
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT correct_answer FROM questions WHERE id = ?", (question_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return jsonify({'error': 'Question not found'}), 404
    correct = result[0]
    is_correct = (user_answer == correct)
    if is_correct:
        c.execute("UPDATE users SET score = score + 10 WHERE username = ? RETURNING score", (current_user,))
        new_score = c.fetchone()[0]
        conn.commit()
        conn.close()
        return jsonify({'correct': True, 'new_score': new_score}), 200
    conn.close()
    return jsonify({'correct': False}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
