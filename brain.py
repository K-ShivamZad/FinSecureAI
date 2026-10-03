import pandas as pd
import difflib

# Global Memory: Context yaad rakhne ke liye
chat_memory = {"last_col": None}

def chat_with_data(df, query):
    global chat_memory
    query_lower = query.lower().strip()
    
    # 1. GREETING HANDLER (Insaano ki tarah baat karne ke liye)
    if query_lower in ['hi', 'hello', 'hey', 'help', 'hi!', 'hello!']:
        return "Hello! I am your FinSecure AI Agent. Ask me to count values (like 'how many sunny'), or find totals, averages, and max values in your data!"

    # 2. DEEP DATA SCANNING (Andar ki values dhoondhne ke liye, jaise "sunny")
    # Yeh loop poore dataset ki string values check karega
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            # Sabhi unique values ko lower case mein le aaye
            unique_values = [str(v).lower() for v in df[col].dropna().unique()]
            for word in query_lower.split():
                if word in unique_values:
                    # Agar value mil gayi, toh turant uska total count nikal kar de dega
                    count = df[df[col].astype(str).str.lower() == word].shape[0]
                    chat_memory["last_col"] = col  # Memory mein column set kar diya
                    return f"I found the value '{word.title()}' in the '{col}' column. It appears {count} times in the dataset."

    # 3. FUZZY MATCHING (Typo correction for columns)
    columns = [str(col).lower() for col in df.columns]
    matched_cols = []
    words = query_lower.split()
    
    for word in words:
        # Cutoff ko 0.6 se gira kar 0.4 kar diya taaki "plyer" -> "playtennis" match ho jaye
        matches = difflib.get_close_matches(word, columns, n=1, cutoff=0.4)
        if matches:
            matched_cols.append(matches[0])
            break # Pehla match milte hi loop rok do
            
    # 4. CONTEXT MEMORY LOGIC
    target_col = None
    if matched_cols:
        target_col = matched_cols[0]
        chat_memory["last_col"] = target_col
    elif chat_memory["last_col"] in columns:
        target_col = chat_memory["last_col"]
        
    if not target_col:
         return f"I couldn't understand which column or value you meant. Available columns are: {', '.join(df.columns)}."

    is_numeric = pd.api.types.is_numeric_dtype(df[target_col])
    
    # 5. DATA SCIENCE MATH OPERATIONS
    if any(word in query_lower for word in ['total', 'sum', 'add']):
        if is_numeric:
            res = df[target_col].sum()
            return f"The total sum of '{target_col}' is {res:,.2f}."
        return f"Column '{target_col}' contains text, so I cannot calculate a sum."
        
    elif any(word in query_lower for word in ['average', 'mean', 'avg']):
        if is_numeric:
            res = df[target_col].mean()
            return f"The average value for '{target_col}' is {res:,.2f}."
        return f"Column '{target_col}' is not numeric."
        
    elif any(word in query_lower for word in ['highest', 'maximum', 'max', 'top']):
        if is_numeric:
            max_val = df[target_col].max()
            return f"The maximum value in '{target_col}' is {max_val:,.2f}."
        return f"Column '{target_col}' is not numeric."
        
    elif any(word in query_lower for word in ['count', 'how many']):
        count = df[target_col].count()
        return f"There are {count} valid records in the '{target_col}' column."
        
    else:
        unique_vals = df[target_col].nunique()
        return f"I am looking at the column '{target_col}'. It has {unique_vals} unique values. You can ask me for its 'total', 'average', 'max', or 'count'."