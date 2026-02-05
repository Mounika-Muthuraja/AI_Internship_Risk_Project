import streamlit as st
import requests
import pdfplumber
import json
import re

st.set_page_config(
    page_title="AI-Powered Internship Risk Detector",
    layout="wide"
)

st.title("🎯 AI-Powered Internship Risk Detection System")

# ------------------------
# SESSION STATE
# ------------------------
if "ai_output" not in st.session_state:
    st.session_state.ai_output = None
if "document_text" not in st.session_state:
    st.session_state.document_text = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "email_body" not in st.session_state:
    st.session_state.email_body = None
if "email_status" not in st.session_state:
    st.session_state.email_status = None

# ------------------------
# Helper: Extract JSON safely
# ------------------------
def extract_json_from_text(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return {}
        return {}

# ------------------------
# AI Analysis Function
# ------------------------
def analyze_with_ai(document_text, user_question):
    api_key = st.secrets["OPENROUTER_API_KEY"]

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "temperature": 0,
            "max_tokens": 600,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Return ONLY valid JSON. No extra text."},
                {
                    "role": "user",
                    "content": f"""
Return JSON in EXACTLY this format:

{{
  "stipend_clarity": "Clear | Unclear",
  "registration_fee": "Yes | No",
  "company_verification": "Verified | Unverified",
  "communication_channel": "Official | Unofficial",
  "risk_level": "Low | Medium | High",
  "risk_reason": "string",
  "summary": "string"
}}

User Question:
{user_question}

Document Text:
{document_text[:6000]}
"""
                }
            ]
        },
        timeout=60
    )

    if response.status_code != 200:
        st.error(response.text)
        return {}

    ai_text = response.json()["choices"][0]["message"]["content"]
    return extract_json_from_text(ai_text)

# ------------------------
# File Upload
# ------------------------
uploaded_file = st.file_uploader(
    "Upload internship offer (.pdf or .txt)",
    type=["pdf", "txt"]
)

# ------------------------
# Extract & Display Document
# ------------------------
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            document_text = "\n".join(
                [p.extract_text() for p in pdf.pages if p.extract_text()]
            )
    else:
        document_text = uploaded_file.read().decode("utf-8")

    st.session_state.document_text = document_text

    st.subheader("📄 Extracted Document Content")
    st.text_area(
        "Extracted Text",
        document_text,
        height=200
    )

    # ------------------------
    # Question Input BELOW extracted text
    # ------------------------
    user_query = st.text_input(
        "Ask your question about this internship",
        placeholder="Is this internship genuine?"
    )

    # ------------------------
    # ASK / ANALYZE BUTTON
    # ------------------------
    if user_query and st.button("🔍 Ask / Analyze"):
        with st.spinner("Analyzing internship document..."):
            st.session_state.ai_output = analyze_with_ai(
                st.session_state.document_text,
                user_query
            )
            st.session_state.analysis_done = True
            st.session_state.email_body = None
            st.session_state.email_status = None

# ------------------------
# SHOW ANALYSIS RESULTS
# ------------------------
if st.session_state.analysis_done and st.session_state.ai_output:
    ai_output = st.session_state.ai_output

    st.subheader("📋 Quick Risk Analysis")

    risk_level = ai_output.get("risk_level", "Unknown")
    if risk_level == "High":
        st.error("⚠️ High Risk Internship Detected")
    else:
        st.success("✅ No major scam indicators detected")

    st.markdown(f"**Risk Level:** {risk_level}")
    st.markdown(f"**Reason:** {ai_output.get('risk_reason', 'Not available')}")
    st.markdown(f"**Summary:** {ai_output.get('summary', '')}")

    st.subheader("🗂 Structured Data Extracted (JSON)")
    st.json(ai_output)

# ------------------------
# EMAIL SECTION
# ------------------------
if st.session_state.analysis_done and st.session_state.ai_output:
    st.subheader("📧 Send Detailed Email Report")

    recipient_email = st.text_input("Recipient Email", key="email_input")

    if st.button("Send Alert / Detailed Report"):
        if not recipient_email:
            st.warning("Please enter recipient email")
        else:
            webhook_url = st.secrets["N8N_WEBHOOK_URL"]
            payload = {
                "recipient": recipient_email,
                "ai_output": json.dumps(st.session_state.ai_output),
                "document_text": st.session_state.document_text,
                "user_query": user_query
            }

            with st.spinner("Sending data to n8n workflow..."):
                try:
                    res = requests.post(webhook_url, json=payload, timeout=60)
                    if res.status_code == 200:
                        st.session_state.email_status = "✅ Alert Email Status: SENT"
                        st.session_state.email_body = f"""
<h2 style="color:red;">⚠️ Internship Risk Alert</h2>
<p><b>Risk Level:</b> {ai_output.get('risk_level')}</p>
<p><b>Reason:</b><br> {ai_output.get('risk_reason')}</p>
<h3>Summary</h3>
<p>{ai_output.get('summary')}</p>
<hr>
<p><b>User Question:</b></p>
<p>{user_query}</p>
<p style="color:red;">This internship shows multiple scam indicators. Please verify carefully before proceeding.</p>
<br>
<p>Generated by AI Internship Risk Detection System</p>
"""
                    else:
                        st.session_state.email_status = f"❌ Email not sent. Webhook error: {res.text}"
                        st.session_state.email_body = None
                except Exception as e:
                    st.session_state.email_status = f"❌ Connection error: {e}"
                    st.session_state.email_body = None

# ------------------------
# DISPLAY GENERATED EMAIL & STATUS
# ------------------------
if st.session_state.email_body:
    st.subheader("✉️ Generated Email Body")
    st.code(st.session_state.email_body, language="html")

if st.session_state.email_status:
    st.subheader("📌 Email Automation Status")
    st.info(st.session_state.email_status)
