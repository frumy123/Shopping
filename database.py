import sqlite3

conn = sqlite3.connect('users.db')  # או השם שמשמש אצלך בקוד
cursor = conn.cursor()

# צרי את הטבלה
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()

print("Database initialized successfully.")
