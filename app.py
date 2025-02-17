# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emss.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Initialize Database ---
db = SQLAlchemy(app)

# --- Define the User model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    area_desk = db.Column(db.String(128))
    photograph = db.Column(db.String(256))
    role = db.Column(db.String(50))  # 'manager' or 'employee'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Routes ---

@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'manager':
            return redirect(url_for('manager_dashboard'))
        elif user.role == 'employee':
            return redirect(url_for('employee_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Process login
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("Logged in successfully!", "success")
            if user.role == 'manager':
                return redirect(url_for('manager_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process signup
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        area_desk = request.form.get('area_desk')
        photograph = request.form.get('photograph')
        role = request.form.get('role')
        if User.query.filter_by(email=email).first():
            flash("User already exists. Please log in.", "error")
            return redirect(url_for('login'))
        new_user = User(name=name, email=email, area_desk=area_desk,
                        photograph=photograph, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/manager')
def manager_dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'manager':
        flash("Access denied. Managers only.", "error")
        return redirect(url_for('login'))
    return render_template('manager.html', user=user)

@app.route('/employee')
def employee_dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if user.role != 'employee':
        flash("Access denied. Employees only.", "error")
        return redirect(url_for('login'))
    return render_template('employee.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# --- Run the App ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
