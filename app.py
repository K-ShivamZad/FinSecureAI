import streamlit as st
import pandas as pd
import plotly.express as px
from db_handler import init_db, create_user, verify_user, load_csv_to_db, get_data

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
    # MAIN DASHBOARD
    st.sidebar.title(f"👤 Admin: {st.session_state.user}")
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", type="secondary"):
        st.session_state.user = None
        st.rerun()

    st.title("📊 FinSecure AI Analytics")
    
    df = get_data(st.session_state.user)
    
    # 1. KPI Metrics (Highly responsive, auto-resizes on mobile)
    if not df.empty:
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Transactions", len(df))
        with kpi2:
            st.metric("Total Volume (₹)", f"{df['amount'].sum():,.2f}")
        with kpi3:
            st.metric("Risk Level", "Low (Phase 1)", delta="Normal", delta_color="normal")
        st.divider()

    # 2. Responsive Layout for Data & Upload
    # Desktop par 2:1 ratio me dikhega, mobile par automatically ek ke niche ek aayega
    left_col, right_col = st.columns([2, 1], gap="large")
    
    with right_col:
        st.subheader("⚙️ Data Engineering")
        # Expander use kiya hai taaki mobile screens par UI clutter na ho
        with st.expander("📤 Upload New Bank Logs (CSV)", expanded=True):
            st.info("Columns required: date, amount, category, description")
            file = st.file_uploader("Drop CSV here", type=['csv'], label_visibility="collapsed")
            
            if file and st.button("Run ETL Pipeline", type="primary"):
                with st.spinner("Processing & Securing Data..."):
                    df_upload = pd.read_csv(file)
                    load_csv_to_db(st.session_state.user, df_upload)
                    st.success("ETL Successful!")
                    st.rerun() # Refresh page to show new data immediately
    
    with left_col:
        st.subheader("🔍 Transaction Intelligence")
        if not df.empty:
            # Plotly chart native responsive hota hai
            fig = px.pie(df, values='amount', names='category', hole=0.4)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig, use_container_width=True) # use_container_width zaruri hai screen fit ke liye
            
            st.write("### 📜 Secure Audit Logs")
            df['masked_desc'] = df['description'].apply(lambda x: str(x)[:4] + "****" if pd.notnull(x) else "")
            
            # hide_index=True se table clean dikhti hai
            st.dataframe(df[['date', 'category', 'amount', 'masked_desc']].tail(5), use_container_width=True, hide_index=True)
        else:
            st.info("Dashboard is empty. Run the ETL pipeline on the right to inject data.")