import sqlite3

# יצירת חיבור למסד הנתונים
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# יצירת טבלת users
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

# שמירת השינויים וסגירת החיבור
connection.commit()
connection.close()

