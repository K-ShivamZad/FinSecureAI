import sqlite3
import pandas as pd
import hashlib
import secrets

DB_NAME = "finsecure.db"

# 1. Data Privacy: Hashing & Salting
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hash_gen = hashlib.sha256((salt + password).encode()).hexdigest()
    return hash_gen, salt

# 2. Database Management System (DBMS) Setup
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT UNIQUE, password_hash TEXT, salt TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, 
                  date TEXT, amount REAL, category TEXT, description TEXT, is_fraud INTEGER DEFAULT 0)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_user ON transactions(username)')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        pw_hash, salt = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, pw_hash, salt))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    res = c.fetchone()
    conn.close()
    if res and hash_password(password, res[1])[0] == res[0]:
        return True
    return False

# 3. Data Engineering (ETL Process)
def load_csv_to_db(username, df):
    conn = sqlite3.connect(DB_NAME)
    df['username'] = username
    df['is_fraud'] = 0 # Default normal for Phase 1
    # Extracts data from CSV and Loads directly to SQL
    df[['username', 'date', 'amount', 'category', 'description', 'is_fraud']].to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()

def get_data(username):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM transactions WHERE username = ?", conn, params=(username,))
    conn.close()
    return df