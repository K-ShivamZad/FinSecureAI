# 🛡️ FinSecure AI: Hybrid Financial Analytics & Fraud Detection

FinSecure AI is an enterprise-grade financial tracking and analytics platform. It uses a **Phased Development Model**, evolving from a secure ETL pipeline and NLP-based logging system (Minor Project) into a fully decoupled, AI-driven fraud detection platform (Capstone Project).

---

## 🚀 Phase 1: Foundation (Minor Project) — *COMPLETED*
This phase focuses on Data Engineering, Information Retrieval (NLP), Database Management, and Data Privacy.

### 🌟 Core Features Implemented:
* **Hybrid Data Input Hub:**
  * **🎙️ Smart NLP Logger:** Integrated `spaCy` for Natural Language Processing. Users can type conversational expenses (e.g., *"Paid 1200 for flight ticket"*), and the system autonomously extracts the amount and categorizes it using keyword lemmatization.
  * **📤 Secure Bulk ETL Pipeline:** Automated Extract-Transform-Load pipeline with strict CSV schema validation. Prevents database corruption and handles server errors gracefully.
* **Security & DBMS:** 
  * Multi-user authentication using **SHA-256 password hashing** with unique salts.
  * Optimized SQLite architecture with Primary/Foreign keys.
  * Frontend **Data Masking** to hide sensitive transaction descriptions (Data Privacy).
* **Interactive Analytics & Budgeting:**
  * Real-time KPIs and dynamic Plotly visualizations.
  * **Budget Tracker:** Users can set monthly goals, triggering dynamic progress bars and visual alerts.
  * **Data Export:** 1-Click "Download Audit Report" functionality for localized CSV backups.
* **Data Science Preparation (Heuristic Labeling):** Built-in rule-based flagging (transactions > ₹50,000) to autonomously generate labeled training data for Phase 2 Machine Learning models.

---

## 🛠️ Technology Stack (Phase 1)
* **Frontend:** Streamlit, Custom CSS
* **Data Processing & Analytics:** Pandas, Plotly Express
* **Information Retrieval (NLP):** spaCy (`en_core_web_sm`), Regex
* **Database & Security:** SQLite3, Hashlib, Secrets

---

## 🚀 Phase 2: Capstone Upgrade — *PLANNED*
The next evolution involves transitioning from a monolithic prototype to a highly scalable microservices architecture.

* **Architecture Overhaul:** Decoupling the system by migrating the backend to **FastAPI** and replacing Streamlit with a Custom JS/HTML frontend.
* **Database Migration:** Upgrading from SQLite to **MySQL** for enterprise-level concurrency and relational integrity.
* **Machine Learning:** Deploying Supervised (Random Forest) or Unsupervised (Isolation Forest) algorithms on the heuristically labeled dataset to detect spending anomalies autonomously.

---

## 🌿 Git Branching Strategy
This repository strictly follows branch-based version control to separate academic evaluation phases:
* **`main` branch (Stable):** Contains the fully tested, deployable Phase 1 (Minor Project) codebase.
* **`capstone-upgrade` branch (Development):** The active workspace for Phase 2 architectural migrations and ML deployments.

---

## ⚙️ Local Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/K-ShivamZad/FinSecureAI.git](https://github.com/K-ShivamZad/FinSecureAI.git)
   cd FinSecureAI