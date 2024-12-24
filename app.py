from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Create templates directory if it doesn't exist
if not os.path.exists('templates'):
    os.makedirs('templates')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        # TODO: Implement actual authentication
        if data['username'] == 'admin' and data['password'] == 'admin':
            session['user_id'] = 1
            session['is_admin'] = True
            return jsonify({'success': True, 'is_admin': True})
        elif data['username'] == 'user' and data['password'] == 'user':
            session['user_id'] = 2
            session['is_admin'] = False
            return jsonify({'success': True, 'is_admin': False})
        return jsonify({'success': False}), 401
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    data = request.get_json()
    # TODO: Implement actual analysis
    # Mock response for now
    return jsonify({
        'healthyPercentage': 75,
        'categories': [
            {'name': 'Natural', 'percentage': 60},
            {'name': 'Additives', 'percentage': 20},
            {'name': 'Preservatives', 'percentage': 15},
            {'name': 'Artificial Colors', 'percentage': 5}
        ]
    })

@app.route('/compare', methods=['POST'])
@login_required
def compare():
    data = request.get_json()
    # TODO: Implement actual comparison
    # Mock response for now
    return jsonify({
        'product1': {
            'healthyPercentage': 75,
            'categories': [
                {'name': 'Natural', 'percentage': 60},
                {'name': 'Additives', 'percentage': 20}
            ]
        },
        'product2': {
            'healthyPercentage': 45,
            'categories': [
                {'name': 'Natural', 'percentage': 40},
                {'name': 'Additives', 'percentage': 35}
            ]
        }
    })

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
