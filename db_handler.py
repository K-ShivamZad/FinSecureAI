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
    
    # NEW: Table to store user budget goals (Integrates Slide 6 of your presentation)
    c.execute('''CREATE TABLE IF NOT EXISTS user_settings 
                 (username TEXT PRIMARY KEY, monthly_budget REAL)''')
                 
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
    """
    ETL Pipeline with Data Validation and Error Handling.
    Checks for structural integrity before executing SQL loads.
    """
    # 1. Testing & Validation: Check if correct columns exist
    required_columns = {'date', 'amount', 'category', 'description'}
    if not required_columns.issubset(set(df.columns)):
        return False, f"Invalid CSV structure. Required columns: {required_columns}"
    
    try:
        conn = sqlite3.connect(DB_NAME)
        df['username'] = username
        
        # Data Science Heuristic Labeling
        df['is_fraud'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        df['is_fraud'] = df['is_fraud'].apply(lambda x: 1 if float(x) > 50000 else 0)
        
        # Load safely to SQL
        df[['username', 'date', 'amount', 'category', 'description', 'is_fraud']].to_sql(
            'transactions', conn, if_exists='append', index=False
        )
        conn.commit()
        return True, "Data securely loaded into Database!"
    
    except Exception as e:
        # Code Optimization: Catching server/DB errors gracefully
        return False, f"Database Error: {str(e)}"
    
    finally:
        # Architecture Planning: Always close connections to prevent memory leaks
        if conn:
            conn.close()