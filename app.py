from flask import Flask, render_template, request, redirect, session, flash, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime
from  predictor import majority_vote_predict
from chatbot.chat_engine import get_response

dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(dotenv_path)

app = Flask(__name__, template_folder="frontend/templates")
app.secret_key = os.getenv("SECRET_KEY")
print("Secret Key:", app.secret_key)
# --- MySQL Connection Setup ---
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn 


@app.route('/')
def home():
    return render_template('home.html')

import re
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        gender = request.form['gender']
        occupation = request.form['occupation']
        city = request.form['city']
        state = request.form['state']

        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            flash('Please enter a valid Gmail address.', 'danger')
            return redirect('/register')

        # Validate password
        if not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$', password):
            flash('Password must be at least 8 characters long, contain one uppercase letter, one number, and one special character.', 'danger')
            return redirect('/register')
        

        # Check if the email already exists in the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already exists. Please use a different email address.', 'danger')
            return redirect('/register')  # Redirect back to the registration page

        try:
            # Insert new user data into users table
            cur.execute(""" 
                INSERT INTO users (full_name, email, password, age, gender, occupation, city, state)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (full_name, email, password, age, gender, occupation, city, state))
            conn.commit()
            user_id = cur.lastrowid
            flash('Registration successful! Please log in.', 'success')
            return redirect('/login')

        except mysql.connector.Error as e:
            flash(f'Error during registration: {e}', 'danger')
            conn.rollback()  # Rollback the transaction if any error occurs
            return redirect('/register')

        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # print(f"Attempting to login with email: {email} and password: {password}")

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
        user = cur.fetchone()
        conn.close()

        # print(f"Query result: {user}")  # Debug print: Check the result of the query

        if user:
            print(f"User found: {user}")  # Debug print
            session['user_id'] = user['user_id']
            flash('Login successful!', 'success')
            return redirect('/predict')
        else:
            flash('Incorrect user ID or password.', 'danger')
            return redirect('/login')

    return render_template('login.html')

@app.route('/predict', methods=['GET','POST'])
def predict():
        
    if request.method=='POST':
        user_id = session.get('user_id')
        
        # Get user email from DB using user_id
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        email = user['email'] if user else None

        # Get form inputs
        Age = float(request.form['Age'])
        Sex = request.form['Sex']
        BP = request.form['BP']
        Cholesterol = request.form['Cholesterol']
        Na = float(request.form['Na'])
        K = float(request.form['K'])  

        user_input = {
            "Age": Age,
            "Sex": Sex,
            "BP": BP,
            "Cholesterol":Cholesterol,
            "Na": Na,
            "K": K
        }

        result = majority_vote_predict(user_input)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions (user_id,user_email,Age, Sex, BP, Cholesterol, Na, K, predicted_drug, predicted_at)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id,email,Age, Sex, BP, Cholesterol, Na, K, result, datetime.now()))
            conn.commit()

        # Fetch history for current user
            cursor = conn.cursor(dictionary=True) 
            cursor.execute("""
                SELECT user_id, Age, Sex, BP, Cholesterol, Na, K, predicted_drug, predicted_at
                FROM predictions WHERE user_id = %s ORDER BY predicted_at DESC LIMIT 5
            """, (user_id,))
            history = cursor.fetchall()

        except Exception as e:
            print("DB Error:", e)
            flash("Prediction failed. Try again later.", "danger")
            return redirect('/')

        cursor.close()
        conn.close() 
        print("Rendering prediction:", result)
        print("History:", history)       
        return render_template('predict.html', prediction=result,history=history)

    return render_template("predict.html", prediction=None)

@app.route("/chatbot", methods=["POST"])
def chatbot_response():
    user_input = request.json.get("message", "")
    response = get_response(user_input)
    return jsonify({"response": response})  

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')    

if __name__ == "__main__":
    app.run(debug=True)
