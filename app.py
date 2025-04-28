import re
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from user_management import add_user, get_user_by_email
from purchase_management import add_purchase_to_csv, get_purchases_by_date, plot_category_expenses, plot_weekly_expenses
from datetime import datetime, timedelta
import pandas as pd
import os
import numpy as np
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Regular expression for validating an Email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        if not re.match(email_regex, email):
            error_message = 'אימייל לא תקין'
        else:
            add_user(email, password)
            return redirect(url_for('login'))
    return render_template('register.html', error_message=error_message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Regular expression for validating an Email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        
        if not re.match(email_regex, email):
            error_message = 'אימייל לא תקין'
        else:
            user = get_user_by_email(email)
            if user and user[2] == password:
                session['email'] = email
                return redirect(url_for('dashboard'))
            else:
                error_message = 'אימייל או סיסמא שגויים'
    return render_template('login.html', error_message=error_message)

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)

    purchases_last_week = get_purchases_by_date(email, start_date, end_date)

    return render_template('dashboard.html', purchases_last_week=purchases_last_week)

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

@app.route('/purchases_by_date', methods=['GET', 'POST'])
def purchases_by_date():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        email = session['email']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        purchases = get_purchases_by_date(email, start_date, end_date)
        print("📅 Start Date:", start_date)
        print("📅 End Date:", end_date)
        print("📦 Found Purchases:", purchases)
        return render_template('dashboard.html', purchases=purchases)
    return render_template('purchases_by_date.html')

@app.route('/saveData', methods=['GET'])
def save_data():
    # הנתונים בדוגמה (תוכל לשנות אותם לפי הצורך)
    email = session['email']
    purchases = get_purchases_by_date(email, datetime.today() - timedelta(days=30), datetime.today())  # לדוגמה קניות בחודש האחרון

    # יצירת DataFrame מתוך הנתונים
    df = pd.DataFrame(purchases, columns=["שם מוצר", "קטגוריה", "כמות", "מחיר", "תאריך"])

    # שמירת ה-DataFrame כקובץ CSV
    file_path = f"backup/{email}_purchases_backup.csv"
    os.makedirs("backup", exist_ok=True)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")

    # החזרת הקובץ למשתמש להורדה
    return send_file(file_path, as_attachment=True, download_name=f"{email}_purchases_backup.csv")


@app.route('/graph1')
def graph1():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    img = plot_weekly_expenses(email)
    image_data = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('graph.html', image_data=image_data, title='הוצאות שבועיות')


@app.route('/graph2')
def graph2():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    img = plot_category_expenses(email)
    image_data = base64.b64encode(img.getvalue()).decode('utf-8')
    return render_template('graph.html', image_data=image_data, title='הוצאות לפי קטגוריה')

@app.route('/demoProfile')
def demo_profile():
    np.random.seed(0)  # לשחזור עקבי של הנתונים

    products = ['לחם', 'חלב', 'ביצים', 'גבינה', 'פסטה', 'אורז', 'מים', 'חטיפים', 'קפה', 'שוקולד']
    categories = ['מזון', 'משקאות', 'מוצרי בסיס']
    dates = pd.date_range(end=pd.Timestamp.today(), periods=7).strftime('%Y-%m-%d')

    data = {
        'שם המוצר': np.random.choice(products, 15),
        'קטגוריה': np.random.choice(categories, 15),
        'כמות': np.random.randint(1, 5, size=15),
        'מחיר': np.round(np.random.uniform(5, 50, size=15), 2),
        'תאריך': np.random.choice(dates, 15)
    }

    df = pd.DataFrame(data)
    purchases = df.values.tolist()  # נשלח לרינדור כ-רשימה של רשימות

    return render_template('demo_dashboard.html', purchases=purchases)

# חסימת פונקציות אחרות בדמו
@app.before_request
def block_other_routes():
    if request.endpoint not in ['demo_profile', 'static', 'register', 'home'] and '/demo' in request.path:
        return redirect(url_for('register'))

# הוספת כפתורים בדף ה-HTML להצגת הגרפים
@app.route('/graphs')
def graphs():
    return render_template('graphs.html')

#חנות להשוואת מחירים
@app.route('/store')
def store():
    return render_template('store.html')

@app.route('/optimize_shopping', methods=['POST'])
def optimize_shopping():
    if 'email' not in session:
        return redirect(url_for('login'))

    # קריאת דף החנות
    with open('templates/store.html', 'r', encoding='utf-8') as f:
        store_html = f.read()

    soup = BeautifulSoup(store_html, 'html.parser')
    products = soup.find_all('div', class_='product')

    store_items = []
    for product in products:
        name = product.find('span', class_='name').text.strip()
        price = float(product.find('span', class_='price').text.strip())
        store_items.append({'name': name, 'price': price})

    # קניות אחרונות של המשתמש
    email = session['email']
    user_purchases = get_purchases_by_date(email, datetime.today() - timedelta(days=30), datetime.today())

    cheaper_items = []
    for purchase in user_purchases:
        product_name = purchase[0]
        user_price = float(purchase[3])

        for store_product in store_items:
            if store_product['name'] == product_name and store_product['price'] < user_price:
                cheaper_items.append({
                    'name': product_name,
                    'old_price': user_price,
                    'new_price': store_product['price']
                })

    return render_template('optimize_result.html', cheaper_items=cheaper_items)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)