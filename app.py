import streamlit as st
import pandas as pd
import plotly.express as px
from db_handler import init_db, create_user, verify_user, load_csv_to_db, get_data, set_budget, get_budget

# page_icon aur layout wide set karne se UI better scale hota hai
st.set_page_config(page_title="FinSecure AI", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")
init_db()

# Custom CSS for Mobile Responsiveness & Premium Look
st.markdown("""
    <style>
    /* Remove extra blank space at the top */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    /* Make buttons full width and rounded for touch devices */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    /* Smooth input fields */
    .stTextInput>div>div>input { border-radius: 8px; }
    /* Enhance metric numbers */
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #1f77b4; }
    </style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: 
    st.session_state.user = None

# GATEWAY (Security)
if not st.session_state.user:
    # Login form ko center me rakhne ke liye 3 columns banaye hain
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🛡️ FinSecure AI</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Admin Secure Gateway</h4>", unsafe_allow_html=True)
        st.write("") # spacing
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("Access Dashboard", type="primary"):
                if verify_user(u, p):
                    st.session_state.user = u
                    st.rerun()
                else: 
                    st.error("Invalid credentials")
                    
        with tab2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Create Admin Account"):
                if create_user(nu, np): 
                    st.success("Created! Please Login.")
                else: 
                    st.error("Username exists.")

else:
    # MAIN DASHBOARD & SIDEBAR
    st.sidebar.title(f"👤 Admin: {st.session_state.user}")
    
    df = get_data(st.session_state.user)
    
    # 1. Practical Feature: Dynamic Date Filtering
    if not df.empty:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📅 Filter Analytics")
        
        # Convert date column to datetime objects safely
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        min_date, max_date = df['date'].min().date(), df['date'].max().date()
        
        # Date range picker
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
        
        # Apply filter if both dates are selected
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
            df = df.loc[mask]

    # 2. Budget Tracker Widget
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Budget Settings")
    current_budget = get_budget(st.session_state.user)
    new_budget = st.sidebar.number_input("Set Monthly Budget (₹)", min_value=0, value=int(current_budget), step=1000)
    
    if st.sidebar.button("Update Budget"):
        set_budget(st.session_state.user, new_budget)
        st.sidebar.success("Budget Saved!")
        st.rerun()
        
    # 3. Practical Feature: 1-Click Audit Export
    if not df.empty:
        st.sidebar.markdown("---")
        csv_export = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="📥 Download Audit Report (CSV)",
            data=csv_export,
            file_name=f"FinSecure_Audit_{st.session_state.user}.csv",
            mime="text/csv",
        )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", type="secondary"):
        st.session_state.user = None
        st.rerun()

    st.title("📊 FinSecure AI Analytics")
    
    # KPI Metrics
    if not df.empty:
        total_spent = df['amount'].sum()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Transactions", len(df))
        with kpi2:
            st.metric("Total Volume (₹)", f"{total_spent:,.2f}")
        with kpi3:
            suspicious_count = len(df[df['is_fraud'] == 1])
            if suspicious_count > 0:
                st.metric("Risk Level", "Elevated", delta=f"{suspicious_count} Alerts", delta_color="inverse")
            else:
                st.metric("Risk Level", "Low (Phase 1)", delta="Normal", delta_color="normal")
        
        if current_budget > 0:
            st.write("### 📈 Budget Utilization")
            progress_fraction = min(total_spent / current_budget, 1.0)
            st.progress(progress_fraction)
            
            if total_spent > current_budget:
                st.error(f"⚠️ Budget Exceeded! You have spent ₹{total_spent:,.2f} out of your ₹{current_budget:,.2f} budget.")
            else:
                st.success(f"✅ On Track! You have spent ₹{total_spent:,.2f} out of your ₹{current_budget:,.2f} budget.")
        st.divider()

    # Responsive Layout for Data & Upload
    left_col, right_col = st.columns([2, 1], gap="large")
    
    with right_col:
        st.subheader("⚙️ Data Engineering")
        with st.expander("📤 Upload New Bank Logs (CSV)", expanded=True):
            st.info("Columns required: date, amount, category, description")
            file = st.file_uploader("Drop CSV here", type=['csv'], label_visibility="collapsed")
            
            if file and st.button("Run ETL Pipeline", type="primary"):
                with st.spinner("Validating & Securing Data..."):
                    df_upload = pd.read_csv(file)
                    
                    # Connected to the new Error Handling function
                    success, message = load_csv_to_db(st.session_state.user, df_upload)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message) # Shows exact validation error without crashing
    
    with left_col:
        st.subheader("🔍 Transaction Intelligence")
        if not df.empty:
            fig = px.pie(df, values='amount', names='category', hole=0.4)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig, use_container_width=True) 
            
            st.write("### 📜 Secure Audit Logs")
            df['masked_desc'] = df['description'].apply(lambda x: str(x)[:4] + "****" if pd.notnull(x) else "")
            
            # Formats date for cleaner viewing
            df['display_date'] = df['date'].dt.strftime('%Y-%m-%d')
            st.dataframe(df[['display_date', 'category', 'amount', 'masked_desc']].tail(5), use_container_width=True, hide_index=True)
            
            suspicious_df = df[df['is_fraud'] == 1]
            if not suspicious_df.empty:
                st.error(f"⚠️ {len(suspicious_df)} Suspicious Transactions Detected (Requires Audit)")
                st.dataframe(suspicious_df[['display_date', 'category', 'amount', 'description']], use_container_width=True, hide_index=True)
        else:
            st.info("Dashboard is empty. Run the ETL pipeline on the right to inject data.")