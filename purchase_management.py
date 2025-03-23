import csv
from datetime import datetime, timedelta

def add_purchase_to_csv(email, product_name, category, quantity, price, date):
    filename = f"{email}.csv"
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([product_name, category, quantity, price, date])

def get_purchases(email):
    filename = f"{email}.csv"
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
    filename = f"{email}.csv"
    purchases = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                purchase_date = datetime.strptime(row[4], '%Y-%m-%d')
                if start_date <= purchase_date <= end_date:
                    purchases.append(row)
    except FileNotFoundError:
        pass
    return purchases