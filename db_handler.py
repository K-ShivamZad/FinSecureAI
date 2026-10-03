import sqlite3
import pandas as pd
import hashlib
import secrets
import datetime
import io
import re

DB_NAME = "finsecure.db"

# ---------------------------------------------------------
# 1. SECURITY & AUTHENTICATION
# ---------------------------------------------------------
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hash_gen = hashlib.sha256((salt + password).encode()).hexdigest()
    return hash_gen, salt

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

# ---------------------------------------------------------
# 2. EXTREME DATABASE INITIALIZATION
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    # Extreme Performance Tuning (SQLite Limits)
    conn.execute("PRAGMA journal_mode = WAL;")  # Write-Ahead Logging for high concurrency
    conn.execute("PRAGMA synchronous = NORMAL;") 
    conn.execute("PRAGMA temp_store = MEMORY;") # RAM processing for speed
    
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT UNIQUE, password_hash TEXT, salt TEXT)''')
                 
    # Master Registry to track all dynamically uploaded datasets
    c.execute('''CREATE TABLE IF NOT EXISTS dataset_registry 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  table_name TEXT UNIQUE, 
                  original_filename TEXT, 
                  upload_date TEXT, 
                  row_count INTEGER, 
                  col_count INTEGER)''')
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. DYNAMIC SCHEMA GENERATION & EXTREME ETL
# ---------------------------------------------------------
def clean_column_names(columns):
    """Removes special characters and spaces to make columns SQLite-safe"""
    clean_cols = []
    for col in columns:
        col = str(col).strip().lower()
        col = re.sub(r'[^a-z0-9_]', '_', col)
        clean_cols.append(col)
    return clean_cols

def process_and_store_universal_data(file_bytes, file_name, username):
    """
    Parses CSV, Excel, JSON, and uses a Custom Robust ARFF Parser.
    Cleans column names, creates SQLite tables, and inserts data.
    """
    import io
    import re
    import pandas as pd
    import datetime
    import sqlite3
    
    DB_NAME = "finsecure.db"
    
    try:
        file_ext = file_name.split('.')[-1].lower()
        
        # 1. Parse Data
        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif file_ext in ['xls', 'xlsx']:
            df = pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
        elif file_ext == 'json':
            df = pd.read_json(io.BytesIO(file_bytes))
        elif file_ext == 'arff':
            # ULTIMATE FIX: Custom ARFF Parser (Bypasses all library errors)
            content = file_bytes.decode('utf-8')
            lines = content.split('\n')
            
            data_started = False
            data_lines = []
            columns = []
            
            for line in lines:
                clean_line = line.strip()
                # Blank lines aur comments (%) ignore karo
                if not clean_line or clean_line.startswith('%'):
                    continue
                    
                # Extract Column Names
                if clean_line.lower().startswith('@attribute'):
                    # Regex to capture column names even if they have spaces/quotes
                    match = re.match(r'(?i)^@attribute\s+([\'"].+?[\'"]|\S+)', clean_line)
                    if match:
                        col_name = match.group(1).strip("'").strip('"')
                        columns.append(col_name)
                        
                # Start reading data after @data tag
                elif clean_line.lower().startswith('@data'):
                    data_started = True
                    
                # Collect CSV data
                elif data_started:
                    data_lines.append(clean_line)
            
            if not data_lines:
                return False, "ARFF Error: No data found after @DATA tag."
                
            # Convert extracted text directly into a Pandas DataFrame
            csv_content = '\n'.join(data_lines)
            # 'na_values' handles missing values marked as '?' in WEKA ARFFs
            df = pd.read_csv(io.StringIO(csv_content), header=None, names=columns, na_values=['?', '', 'NA'])
            
        else:
            return False, f"Unsupported format: .{file_ext}"

        # 2. Dynamic Schema Processing (Make columns SQLite safe)
        def clean_column_names(cols):
            clean_cols = []
            for col in cols:
                col = str(col).strip().lower()
                col = re.sub(r'[^a-z0-9_]', '_', col)
                clean_cols.append(col)
            return clean_cols
            
        df.columns = clean_column_names(df.columns)
        
        # Unique table name generator based on user and timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = f"data_{username}_{timestamp}"
        
        # 3. Extreme Data Load (Using Pandas to_sql directly for schema creation)
        conn = sqlite3.connect(DB_NAME)
        
        df.to_sql(table_name, conn, if_exists='replace', index=False, chunksize=10000)
        
        # 4. Register the new dataset in the Master Catalog
        c = conn.cursor()
        c.execute('''INSERT INTO dataset_registry 
                     (username, table_name, original_filename, upload_date, row_count, col_count) 
                     VALUES (?, ?, ?, ?, ?, ?)''', 
                  (username, table_name, file_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), df.shape[0], df.shape[1]))
        
        conn.commit()
        conn.close()
        
        return True, f"Dataset securely processed and saved as '{table_name}' in SQLite."

    except Exception as e:
        return False, f"Extreme DB Error: {str(e)}"
# ---------------------------------------------------------
# 4. DATA RETRIEVAL FOR UNIVERSAL ANALYZER
# ---------------------------------------------------------
def get_user_datasets(username):
    """Returns a list of all datasets uploaded by the user"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT table_name, original_filename, upload_date, row_count FROM dataset_registry WHERE username = ? ORDER BY id DESC", conn, params=(username,))
    conn.close()
    return df

def load_dataset_from_db(table_name):
    """Loads a specific dynamically generated table back into Pandas for EDA/Visualization"""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

def delete_dataset(username, table_name):
    """Deletes the dynamically generated table to free up space and removes its registry entry."""
    import sqlite3
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 1. Main data table ko drop karo (Isse memory instantly free hoti hai)
        c.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # 2. Registry se us file ka record mita do
        c.execute("DELETE FROM dataset_registry WHERE username = ? AND table_name = ?", (username, table_name))
        
        conn.commit()
        conn.close()
        return True, "Dataset permanently deleted from system!"
    except Exception as e:
        return False, f"Delete Error: {str(e)}"