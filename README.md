🛡️ FiscalNet AI: Pre-Payment Fraud Blocker
**FiscalNet AI** is an advanced forensic auditing system designed to detect and block fraudulent government/corporate transactions *before* payment is released. Unlike traditional post-audit systems, FiscalNet uses a **Tri-Layer Intelligence Engine** combining Graph Theory, Machine Learning (Isolation Forest), and Statistical Rules to flag corruption in real-time.
 Key Features

### 1.  Layer 1: Network Collusion Detection
- Uses **Graph Theory (NetworkX)** to identify hidden links between Officers and Vendors.
- Detects **Direct Collusion** (Shared Phone Numbers/Addresses).
- Visualizes suspicious connections in a real-time graph.

### 2.  Layer 2: AI Anomaly Detection
- Uses **Isolation Forest (Unsupervised ML)** to learn standard transaction patterns.
- Flags **Outliers** (Abnormally high amounts or irregular patterns).
- Hard-coded safety thresholds (e.g., transactions > ₹1 Crore).

### 3.  Layer 3: Statistical & Rule-Based Checks
- **Smurfing Detection:** Catches vendors splitting large bills into small amounts to bypass approval limits.
- **Benford’s Law:** Checks for unnatural number patterns (e.g., amounts starting with 9 to evade limits).
- **Shell Company Check:** Flags vendors registered less than 60 days ago.

### 4.  AI Forensic Analyst (Powered by Gemini 2.0)
- An integrated Chatbot that reads the entire transaction database.
- Ask questions like *"Who is the most corrupt officer?"* or *"Show me suspicious vendors."*

### 5.  Automated Reporting
- Generates instant **PDF Forensic Reports**.
- Prioritizes "Blocked" transactions at the top for immediate auditor attention.

---

##  Tech Stack

- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn (Isolation Forest)
- **Graph Analytics:** NetworkX
- **AI/LLM:** Google Gemini 2.0 Flash/Pro
- **Visualization:** Matplotlib
- **Reporting:** FPDF

---

##  Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/Karan8989-ux/FiscalNet-AI.git](https://github.com/Karan8989-ux/FiscalNet-AI.git)
    cd FiscalNet-AI
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup API Key**
    - Open `app.py`.
    - Find line 16: `GEMINI_API_KEY = "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE"`.
    - Replace it with your Google Gemini API Key.

4.  **Generate Synthetic Data**
    Run the data generator to create a fresh dataset of Officers, Vendors, and Transactions.
    ```bash
    python data_gen.py
    ```

5.  **Run the Application**
```bash
    streamlit run app.py
    ```
    ##🔮 Future Scope
- **Blockchain Integration:** To make the transaction ledger immutable.
- **OCR Integration:** To scan physical invoices directly.
- **Geo-Fencing:** To check if Vendor Address matches the project site.

---

### Created by **Team Sentinel** 🛡️
*Hackathon 2026 Submission*
    ```bash
    streamlit run app.py
    ```
    Reqyuirements to install before
streamlit
pandas
networkx
matplotlib
fpdf
google-generativeai
faker
scikit-learn
