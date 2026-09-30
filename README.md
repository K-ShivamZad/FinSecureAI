# 🛡️ FinSecure AI: Intelligent Financial & Fraud Analytics

FinSecure AI is an enterprise-grade financial tracking and analytics platform. It is being developed using a **Phased Development Model**, evolving from a secure ETL pipeline and database management system into a fully autonomous, AI-driven fraud detection platform.

---

## 🚀 Development Roadmap

### Phase 1: Foundation (Minor Project) — *ACTIVE*
Focuses on Data Engineering, Database Management, and Data Privacy.
* **Secure Access Terminal:** Multi-user authentication system utilizing SHA-256 password hashing with unique salts (Data Privacy & Security).
* **Data Engineering (ETL):** Automated pipeline to Extract raw bank logs (CSV), Transform messy records, and Load them directly into a relational database.
* **DBMS Architecture:** Optimized SQLite schema with Primary/Foreign keys and index structures (`idx_user`) for rapid data retrieval.
* **Real-Time Analytics Dashboard:** Responsive Streamlit interface featuring interactive Plotly visualizations and real-time Key Performance Indicators (KPIs).
* **Data Masking:** Dynamic masking of sensitive transaction descriptions on the frontend to prevent data leaks.

### Phase 2: Intelligence & Optimization (Capstone Upgrade) — *PLANNED*
Focuses on Machine Learning, Advanced Algorithms, and Information Retrieval.
* **Machine Learning Fraud Detection:** Integration of Random Forest / Isolation Forest models to autonomously flag suspicious transactions based on spending anomalies.
* **Data Structures & Algorithms (DSA):** 
  * Implementation of a **Trie Data Structure** for lightning-fast, auto-complete search functionality.
  * Custom **Binary Search** implementation for highly optimized date-range filtering, bypassing standard linear scans.
* **Information Retrieval (IR):** NLP-powered search engine allowing users to query the database using natural language (e.g., *"Show me high-risk transactions from last week"*).

---

## 🛠️ Technology Stack
* **Frontend:** Streamlit, Custom CSS
* **Data Visualization:** Plotly Express
* **Data Processing:** Pandas (ETL Pipeline)
* **Database & Security:** SQLite3, Hashlib, Secrets
* **Machine Learning:** Scikit-Learn *(Phase 2)*

---

## ⚙️ Local Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/K-ShivamZad/FinSecureAI.git](https://github.com/K-ShivamZad/FinSecureAI.git)
   cd FinSecureAI