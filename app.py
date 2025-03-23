from flask import Flask, render_template, request, redirect, url_for, session
from user_management import add_user, get_user_by_email
from purchase_management import add_purchase_to_csv, get_purchases, get_purchases_by_date
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        add_user(email, password)
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_email(email)
        if user and user[2] == password:
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return 'אימייל או סיסמא שגויים'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    purchases = get_purchases(email)
    return render_template('dashboard.html', purchases=purchases)

@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        email = session['email']
        product_name = request.form['product_name']
        category = request.form['category']
        quantity = request.form['quantity']
        price = request.form['price']
        date = request.form['date']
        add_purchase_to_csv(email, product_name, category, quantity, price, date)
        return redirect(url_for('dashboard'))
    return render_template('add_purchase.html')

@app.route('/purchases_last_week')
def purchases_last_week():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    purchases = get_purchases_by_date(email, start_date, end_date)
    return render_template('dashboard.html', purchases=purchases)

@app.route('/purchases_by_date', methods=['GET', 'POST'])
def purchases_by_date():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        email = session['email']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        purchases = get_purchases_by_date(email, start_date, end_date)
        return render_template('dashboard.html', purchases=purchases)
    return render_template('purchases_by_date.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)