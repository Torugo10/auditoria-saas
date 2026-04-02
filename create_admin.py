import sqlite3
import hashlib

# Connect to the SQLite database
conn = sqlite3.connect('/tmp/auditoria_multi_tenant.db')
c = conn.cursor()

# Creating the users table if it doesn't exist
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    nome_completo TEXT NOT NULL,
    ativo INTEGER NOT NULL
)
''')

# Insert admin user function
def insert_admin_user():
    login = 'Admin.Victor'
    password = 'SenhaForte2026'
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    email = 'victor.fetosa@gmail.com'
    nome_completo = 'Victor Hugo'
    ativo = 1

    c.execute('''INSERT INTO users (login, password_hash, email, nome_completo, ativo) VALUES (?, ?, ?, ?, ?)''', (login, password_hash, email, nome_completo, ativo))
    conn.commit()
    print('Admin user created successfully!')

# Calling the function to insert admin user
insert_admin_user()

# Closing the database connection
conn.close()