import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import logic  # logic.py
import time
from fpdf import FPDF
import google.generativeai as genai

# ==========================================
# 🛑 HARDCODED API KEY (BACKEND)
# ==========================================
GEMINI_API_KEY = "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE"

# ==========================================
# 1. PAGE SETUP & UI THEME
# ==========================================
st.set_page_config(page_title="FiscalNet AI", page_icon="🛡️", layout="wide")

if "chat_open" not in st.session_state:
    st.session_state.chat_open = False

st.markdown("""
    <style>
    .stApp {
        background-image: url("https://c1.wallpaperflare.com/preview/467/663/434/technology-background-image-dark.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .block-container, div[data-testid="stMarkdownContainer"], div[data-testid="metric-container"] {
        background-color: rgba(13, 17, 23, 0.9) !important;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMetricValue"] {
        color: #00e5ff !important;
    }
    .watermark {
        position: fixed;
        bottom: 15px;
        right: 90px;
        color: #00e5ff;
        font-family: 'Courier New', Courier, monospace;
        font-size: 20px;
        font-weight: bold;
        background-color: rgba(0, 0, 0, 0.8);
        padding: 8px 20px;
        border-radius: 5px;
        z-index: 999;
        border: 2px solid #00e5ff;
        text-shadow: 0 0 10px #00e5ff;
    }
    .floating-chat-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    .chat-window-container {
        position: fixed;
        bottom: 90px;
        right: 20px;
        width: 400px;
        max-height: 500px;
        background-color: rgba(13, 17, 23, 0.95);
        border: 2px solid #00e5ff;
        border-radius: 15px;
        padding: 15px;
        z-index: 1000;
        overflow-y: auto;
    }
    </style>
    <div class="watermark">CREATED BY SENTINEL TEAM</div>
    """, unsafe_allow_html=True)

st.title("🛡️ FiscalNet: Pre-Payment Fraud Blocker")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def load_data():
    try:
        ven = pd.read_csv("data/vendors.csv")
        off = pd.read_csv("data/officers.csv")
        txn = pd.read_csv("data/transactions.csv")
        return ven, off, txn
    except:
        st.error("❌ Data files missing! Run 'data_gen.py' first.")
        return None, None, None

df_ven, df_off, df_txn = load_data()

# ==========================================
# 3. PDF GENERATOR (CLEAN & FIXED)
# ==========================================
def create_pdf(data_list, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Cleaner Function
    def clean_text(text):
        return str(text).encode('latin-1', 'ignore').decode('latin-1')

    pdf.cell(0, 10, clean_text(title), ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
    headers = ["Vendor", "Officer", "Amount", "Status", "Risk Detail"]
    col_widths = [40, 40, 30, 30, 50]
    
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 10, clean_text(h), 1, 0, 'C', 1)
    pdf.ln()
    
    pdf.set_text_color(0, 0, 0)
    for row in data_list:
        # Status Logic
        status = "BLOCKED" if row['risk_score'] >= 50 else "APPROVED"
        
        v_name = clean_text(str(row['vendor_name'])[:18])
        o_name = clean_text(str(row['officer_name'])[:18])
        amt = clean_text(str(row['amount']))
        risk_log = clean_text(str(row['logs'][0])[:25])
        
        pdf.cell(40, 10, v_name, 1)
        pdf.cell(40, 10, o_name, 1)
        pdf.cell(30, 10, amt, 1)
        pdf.cell(30, 10, status, 1)
        pdf.cell(50, 10, risk_log, 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 4. SIDEBAR INPUTS
# ==========================================
st.sidebar.header("📝 Auditor Console")

if GEMINI_API_KEY == "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE":
    st.sidebar.error("⚠️ API Key not configured in backend code!")

if df_ven is not None:
    vendor_options = [f"{row['Vendor_ID']} - {row['Company']}" for _, row in df_ven.iterrows()]
    selected_ven_full = st.sidebar.selectbox("Select Vendor", vendor_options)
    vendor_id = selected_ven_full.split(" - ")[0]

    officer_options = [f"{row['Officer_ID']} - {row['Name']}" for _, row in df_off.iterrows()]
    selected_off_full = st.sidebar.selectbox("Select Officer", officer_options)
    officer_id = selected_off_full.split(" - ")[0]

    invoice_amount = st.sidebar.number_input("Invoice Amount (Rs.)", min_value=1000, value=50000, step=5000)

    st.sidebar.markdown("---")
    scan_clicked = st.sidebar.button("🔍 Scan & Verify Invoice", type="primary")

    st.sidebar.markdown("---")
    if st.sidebar.button("📄 Download Full Report"):
        with st.spinner("Analyzing ALL transactions (This may take a moment)..."):
            full_data = []
            
            # FIX: Using ALL transactions instead of head(50)
            # We reverse the list to see the newest (Fraud) cases first
            for _, row in df_txn.iloc[::-1].iterrows():
                r_vid, r_oid, r_amt = row['Vendor_ID'], row['Officer_ID'], row['Amount']
                
                # Fetch Names safely
                v_row = df_ven[df_ven['Vendor_ID']==r_vid]
                o_row = df_off[df_off['Officer_ID']==r_oid]
                
                v_name = v_row['Company'].values[0] if not v_row.empty else r_vid
                o_name = o_row['Name'].values[0] if not o_row.empty else r_oid
                
                status, score, r_logs = logic.run_fraud_scan(r_vid, r_oid, r_amt, df_ven, df_off, df_txn)
                full_data.append({"vendor_name":v_name, "officer_name":o_name, "amount":r_amt, "risk_score":score, "logs":r_logs})
            
            # SORTING: Put High Risk (Fraud) at the TOP of the PDF
            full_data.sort(key=lambda x: x['risk_score'], reverse=True)
            
            pdf_bytes = create_pdf(full_data, "FiscalNet - Full Dataset Scan")
            st.sidebar.download_button("📥 Save PDF", data=pdf_bytes, file_name="Full_Fraud_Report.pdf", mime="application/pdf")

# ==========================================
# 5. MAIN DASHBOARD LOGIC
# ==========================================
if not scan_clicked:
    st.markdown("### 📊 Live System Overview")
    total_txns = len(df_txn)
    high_risk_count = int(total_txns * 0.15)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Active Vendors", len(df_ven))
    m2.metric("Monitored Officers", len(df_off))
    m3.metric("Total Transactions", total_txns)
    m4.metric("Potential Risks", f"{high_risk_count}", delta="Attention Required", delta_color="inverse")
    
    st.info("👈 Select details from the sidebar to perform a forensic scan on a specific invoice.")
    st.subheader("Recent Ledger Activity")
    st.dataframe(df_txn.tail(5), use_container_width=True)

else:
    with st.spinner('📄 OCR Scanning Invoice... Extracting Metadata...'):
        time.sleep(1)
    with st.spinner('🧠 Running Tri-Layer Intelligence Engine...'):
        time.sleep(0.5)

    final_status, risk_score, logs = logic.run_fraud_scan(vendor_id, officer_id, invoice_amount, df_ven, df_off, df_txn)

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Risk Score", f"{risk_score}/100", delta="Critical" if risk_score > 50 else "Safe", delta_color="inverse")
    kpi2.metric("Vendor ID", vendor_id)
    kpi3.metric("Inv. Amount", f"₹{invoice_amount:,}")
    
    st.markdown("---")

    col_graph, col_chart = st.columns([1, 1])

    with col_graph:
        st.subheader("🕸️ Collusion Graph")
        G_viz = nx.Graph()
        node_color = '#ff4b4b' if risk_score >= 50 else '#00cc00'
        edge_color = '#ff4b4b' if risk_score >= 50 else (1, 1, 1, 0.2)
        
        G_viz.add_node("Vendor", label=vendor_id)
        G_viz.add_node("Officer", label=officer_id)
        G_viz.add_edge("Vendor", "Officer")
        
        fig, ax = plt.subplots(figsize=(4, 3))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none") 
        
        pos = nx.spring_layout(G_viz)
        nx.draw(G_viz, pos, with_labels=True, node_color=node_color, 
                node_size=2500, font_color='white', font_weight='bold', edge_color=edge_color, width=3, ax=ax)
        st.pyplot(fig)

    with col_chart:
        st.subheader("📊 Anomaly Detection")
        hist_data = df_txn['Amount'].sample(n=min(30, len(df_txn))).tolist()
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        fig2.patch.set_alpha(0)
        ax2.set_facecolor("none")
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.tick_params(colors='white')
        
        ax2.scatter(range(len(hist_data)), hist_data, color='#00e5ff', alpha=0.6, label='History')
        ax2.scatter([len(hist_data)], [invoice_amount], color='#ff4b4b' if risk_score > 30 else '#00cc00', s=150, edgecolors='white', label='Current', linewidth=2)
        legend = ax2.legend(facecolor='black', labelcolor='white')
        st.pyplot(fig2)

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.info(f"**Network:** {logs[0]}")
    c2.info(f"**AI Model:** {logs[1]}")
    c3.info(f"**Stats:** {logs[2]}")
    c4.info(f"**Shell Check:** {logs[3]}")

    st.markdown("---")
    if final_status == "BLOCKED":
        st.markdown("""
            <div style='background-color: rgba(255, 75, 75, 0.2); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #ff4b4b;'>
                <h2 style='color: #ff4b4b; margin:0;'>🚫 PAYMENT BLOCKED</h2>
                <p style='color: white;'>High Fraud Risk Detected. Auto-Freeze Initiated.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background-color: rgba(0, 204, 0, 0.2); padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #00cc00;'>
                <h2 style='color: #00cc00; margin:0;'>✅ APPROVED</h2>
                <p style='color: white;'>No Anomalies Found. Safe to Process.</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. FLOATING AI CHATBOT
# ==========================================
st.markdown('<div class="floating-chat-container">', unsafe_allow_html=True)
if st.button("💬", key="chat_toggle_btn", help="Click to chat with AI Analyst"):
    st.session_state.chat_open = not st.session_state.chat_open
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<script>
    var elements = window.parent.document.querySelectorAll('button[kind="secondary"]');
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].innerText === "💬") {
            elements[i].classList.add("chat-toggle-btn");
        }
    }
</script>
""", unsafe_allow_html=True)

if st.session_state.chat_open:
    st.markdown('<div class="chat-window-container">', unsafe_allow_html=True)
    st.subheader("🤖 AI Forensic Analyst")
    
    if GEMINI_API_KEY == "PASTE_YOUR_REAL_GEMINI_API_KEY_HERE" or not GEMINI_API_KEY:
        st.error("⚠️ API Key not configured in code.")
    else:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            role_color = "#00e5ff" if message["role"] == "assistant" else "#ffab00"
            st.markdown(f"<strong style='color:{role_color}'>{message['role'].title()}:</strong> {message['content']}", unsafe_allow_html=True)

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Ask about vendors, officers, or patterns...", key="user_chat_input")
            submit_chat = st.form_submit_button("Send")

        if submit_chat and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel("gemini-flash-latest")
                
                context = f"""
                Act as a fraud detection expert. Analyze this summary data:
                Total Vendors: {len(df_ven)}, Total Officers: {len(df_off)}, Total Txns: {len(df_txn)}.
                Vendor sample: {df_ven.head(5).to_dict()}
                Officer sample: {df_off.head(5).to_dict()}
                High value txns: {df_txn[df_txn['Amount']>500000].head(5).to_dict()}
                User Question: {user_input}
                Keep answer concise and data-driven.
                """
                with st.spinner("AI Analyzing..."):
                    response = model.generate_content(context)
                    bot_reply = response.text
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.rerun()
            except Exception as e:
                st.error(f"AI Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)