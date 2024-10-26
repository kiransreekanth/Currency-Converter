from flask import Flask, render_template, request, redirect, url_for, session
import requests
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
db_config = {
    'user': 'root',
    'password': 'abc123',
    'host': 'localhost',
    'database': 'currency_conversion',
}

# Function to create a user (used during registration)
def create_user(username, email, password):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                   (username, email, hashed_password))

    conn.commit()
    cursor.close()
    conn.close()

# Index route (Home page)
@app.route('/')
def index():
    if 'loggedin' in session:
        currencies = get_currencies()
        return render_template('index.html', currencies=currencies, result=None)
    return redirect(url_for('login'))

# Data Services route
@app.route('/data_services')
def data_services():
    if 'loggedin' in session:
        # Example functionality: List recent conversion transactions
        transactions = get_recent_transactions(session['username'])
        return render_template('data_services.html', transactions=transactions)
    return redirect(url_for('login'))

# Help route
@app.route('/help')
def help_page():
    return render_template('help.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            user = get_user(username)
            if user and check_password_hash(user['password'], password):
                session['loggedin'] = True
                session['username'] = username
                return redirect(url_for('index'))
            else:
                error = 'Invalid credentials, please try again.'
                return render_template('user.html', error=error)
        else:
            error = 'Please provide both username and password'
            return render_template('user.html', error=error)

    return render_template('user.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Debugging: Print the values to ensure they are being sent correctly
        print(f"Username: {username}, Email: {email}, Password: {password}, Confirm Password: {confirm_password}")

        # Ensure that both passwords are not empty and match
        if not password or not confirm_password:
            error = "Both password fields are required."
            return render_template('registration.html', error=error)

        if password != confirm_password:
            error = "Passwords do not match."
            return render_template('registration.html', error=error)

        # Check if all fields are filled
        if not username or not email or not password:
            error = "All fields are required."
            return render_template('registration.html', error=error)

        # Check if the username already exists in the database
        existing_user = get_user(username)
        if existing_user:
            error = "Username already exists. Please choose a different username."
            return render_template('registration.html', error=error)

        # If everything is good, create the user
        create_user(username, email, password)
        return redirect(url_for('login'))

    return render_template('registration.html')


# Currency converter route
@app.route('/convert', methods=['POST'])
def convert():
    amount = float(request.form['amount'])
    from_currency = request.form['from_currency']
    to_currency = request.form['to_currency']

    API_KEY = "864d39ee0a6753137df0c6fb"
    API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}"

    response = requests.get(API_URL)
    currencies = get_currencies()

    if response.status_code == 200:
        data = response.json()
        if data['result'] == "success":
            rate = data['conversion_rate']
            result = amount * rate
            store_conversion_history(session['username'], from_currency, to_currency, amount, result)
            return render_template('index.html', currencies=currencies, result=f"{amount} {from_currency} = {result:.2f} {to_currency}")
        else:
            result = "Error: Could not fetch conversion rate."
    else:
        result = "Error: Unable to connect to the API."

    return render_template('index.html', currencies=currencies, result=result)

# Utility functions
def get_currencies():
    return [
        {"currency_code": "USD", "currency_name": "US Dollar"},
        {"currency_code": "EUR", "currency_name": "Euro"},
        {"currency_code": "GBP", "currency_name": "British Pound"},
        {"currency_code": "JPY", "currency_name": "Japanese Yen"},
        {"currency_code": "INR", "currency_name": "Indian Rupee"},
        {"currency_code": "AUD", "currency_name": "Australian Dollar"},
        {"currency_code": "CAD", "currency_name": "Canadian Dollar"}
    ]

def get_user(username):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_recent_transactions(username):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(''' 
        SELECT from_currency, to_currency, amount, result, transaction_date 
        FROM transactions 
        JOIN users ON transactions.user_id = users.id 
        WHERE users.username = %s 
        ORDER BY transaction_date DESC 
        LIMIT 5
    ''', (username,))
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return transactions

def store_conversion_history(username, from_currency, to_currency, amount, result):
    user = get_user(username)
    user_id = user['id']
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO transactions (user_id, from_currency, to_currency, amount, result)
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_id, from_currency, to_currency, amount, result))
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
