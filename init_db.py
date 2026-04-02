import hashlib
import sqlite3

def initialize_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Create a users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        login TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )''')

    # Hash the password using SHA256
    password = 'SenhaForte2026'
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Insert the admin user
    cursor.execute('''INSERT OR IGNORE INTO users (login, password) VALUES (?, ?)''',
                   ('Admin.Victor', hashed_password))

    # Commit and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()