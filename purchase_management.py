import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
from matplotlib import rcParams
import pandas as pd
import os
import arabic_reshaper
from bidi.algorithm import get_display

# הגדרת פונט עברי
rcParams['font.family'] = 'David'
rcParams['axes.unicode_minus'] = False


def add_purchase_to_csv(email, product_name, category, quantity, price, date):
    os.makedirs('data', exist_ok=True)
    filename = f"data/{email}_purchases.csv"

    file_exists = os.path.exists(filename)

    with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # כתיבת כותרות אם הקובץ חדש
        if not file_exists:
            writer.writerow(["שם מוצר", "קטגוריה", "כמות", "מחיר", "תאריך"])

        writer.writerow([product_name, category, quantity, price, date])

def get_purchases(email):
    filename = f"data/{email}_purchases.csv"
    purchases = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                purchases.append(row)
    except FileNotFoundError:
        pass
    return purchases


def get_purchases_by_date(email, start_date, end_date):
    file_path = f'data/{email}_purchases.csv'
    if not os.path.exists(file_path):
        return []

    df = pd.read_csv(file_path)
    df['תאריך'] = pd.to_datetime(df['תאריך'], format='%Y-%m-%d', errors='coerce')  # חשוב!
    df = df.dropna(subset=['תאריך'])

    # השורה החשובה - פורמט תאריך בלבד
    df['תאריך'] = df['תאריך'].dt.strftime('%Y-%m-%d')

    mask = (pd.to_datetime(df['תאריך']) >= start_date) & (pd.to_datetime(df['תאריך']) <= end_date)
    return df[mask][["שם מוצר", "קטגוריה", "כמות", "מחיר", "תאריך"]].values.tolist()


def get_monthly_expenses(email):
    purchases = get_purchases(email)
    monthly_expenses = {}
    for purchase in purchases:
        date = datetime.strptime(purchase[4], '%Y-%m-%d')
        month = date.strftime('%Y-%m')
        expense = float(purchase[3]) * int(purchase[2])
        if month in monthly_expenses:
            monthly_expenses[month] += expense
        else:
            monthly_expenses[month] = expense
    return monthly_expenses


def get_category_expenses_for_month(email, month):
    purchases = get_purchases(email)
    category_expenses = {}
    for purchase in purchases:
        date = datetime.strptime(purchase[4], '%Y-%m-%d')
        purchase_month = date.strftime('%Y-%m')
        if purchase_month == month:
            category = purchase[1]
            expense = float(purchase[3]) * int(purchase[2])
            if category in category_expenses:
                category_expenses[category] += expense
            else:
                category_expenses[category] = expense
    return category_expenses


def get_current_vs_average_expenses(email):
    monthly_expenses = get_monthly_expenses(email)
    current_month = datetime.today().strftime('%Y-%m')
    current_expenses = monthly_expenses.get(current_month, 0)
    previous_months_expenses = [expense for month, expense in monthly_expenses.items() if month != current_month]
    average_expenses = sum(previous_months_expenses) / len(previous_months_expenses) if previous_months_expenses else 0
    return current_expenses, average_expenses

# גרפים  ההוצאות כל שבוע בשנה האחרונה
def plot_weekly_expenses(email):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    purchases = get_purchases_by_date(email, start_date, end_date)

    df = pd.DataFrame(purchases, columns=['product_name', 'category', 'quantity', 'price', 'date'])
    df['week'] = pd.to_datetime(df['date']).dt.isocalendar().week
    df['price'] = pd.to_numeric(df['price'], errors='coerce') * pd.to_numeric(df['quantity'], errors='coerce')

    weekly_expenses = df.groupby('week')['price'].sum()

    plt.figure(figsize=(10, 6))
    weekly_expenses.plot(kind='bar', color='blue')
    plt.title(reshape('סך ההוצאות בכל שבוע בשנה האחרונה'))
    plt.xlabel(reshape('שבוע'))
    plt.ylabel(reshape('סך ההוצאות'))

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return img


# פונקציה להפקת גרף עוגה המציג את ההוצאות לכל קטגוריה
def plot_category_expenses(email):
    today = datetime.today()
    start_date = today.replace(day=1)
    end_date = today
    purchases = get_purchases_by_date(email, start_date, end_date)

    df = pd.DataFrame(purchases, columns=['product_name', 'category', 'quantity', 'price', 'date'])
    df['price'] = pd.to_numeric(df['price'], errors='coerce') * pd.to_numeric(df['quantity'], errors='coerce')

    category_expenses = df.groupby('category')['price'].sum()
    labels = [reshape(str(cat)) for cat in category_expenses.index]

    plt.figure(figsize=(8, 8))
    plt.pie(category_expenses, labels=labels, autopct='%1.1f%%',
        colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
    plt.title(reshape('הוצאות לפי קטגוריות'))

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return img


def reshape(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text