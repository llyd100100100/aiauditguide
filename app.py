import streamlit as st
import pandas as pd
import os
from security_utils import SecurityEngine
from ai_utils import AIEngine
from auth_utils import AuthManager
from cloud_utils import CloudManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="AI-Audit-Reviewer",
    page_icon="🛡️",
    layout="wide"
)

def login_page(auth):
    st.title("🛡️ Secure Access")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                success, user = auth.login_user(email, password)
                if success:
                    st.session_state['user'] = user
                    st.rerun()
                else:
                    st.error(f"Login failed: {user}")

    with tab2:
        with st.form("register_form"):
            new_email = st.text_input("Email")
            new_name = st.text_input("Name")
            new_password = st.text_input("Password", type="password")
            new_password_confirm = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if new_password != new_password_confirm:
                    st.error("Passwords do not match")
                else:
                    success, msg = auth.register_user(new_email, new_password, new_name)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration failed: {msg}")

def main_app(user):
    # Handle both Supabase User object and local dict fallback
    if isinstance(user, dict):
        user_name = user.get("user_metadata", {}).get("full_name", "Admin")
        user_email = user.get("email", "admin@local")
    else:
        user_name = user.user_metadata.get('full_name', 'User')
        user_email = user.email

    st.sidebar.markdown(f"**User:** {user_name} ({user_email})")
    if st.sidebar.button("Logout"):
        st.session_state['user'] = None
        st.rerun()

    st.title("🛡️ AI-Audit-Reviewer (Phase 1 Beta)")
    st.markdown("""
    **Smart Assistant for Security Audit** (Prototype)

    This tool helps you analyze audit logs using Google Gemini Flash.

    - **🔍 Smart Analysis**: Detect anomalies and summarize events instantly.
    - **💬 Interactive Chat**: Ask questions about your logs in natural language.
    - **🔒 Privacy First**: Sensitive personal information (PII) is masked locally before analysis.

    ---
    *Note: This is an early prototype for testing purposes.* **Contact:** Questions or feedback? Reach out to [llyd100100100@gmail.com](mailto:llyd100100100@gmail.com)
    """)

    auth = AuthManager() # For cloud access access
    cloud = CloudManager()

    # --- Configuration ---
    # API Key Handling (Auto load from .env or Secrets)
    env_api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    api_key_input = ""
    
    if env_api_key:
        st.sidebar.success("✅ API Key loaded")
        os.environ["GEMINI_API_KEY"] = env_api_key
    else:
        api_key_input = st.sidebar.text_input("Gemini API Key", type="password")
        if api_key_input:
            os.environ["GEMINI_API_KEY"] = api_key_input

    # API Model Selection
    model_options = {
        "Gemini 2.0 Flash (Balanced - 2K RPM)": "gemini-2.0-flash",
        "Gemini 2.0 Flash Lite (High Speed - 4K RPM)": "gemini-2.0-flash-lite",
        "Gemini 1.5 Flash (Stable - 1K RPM)": "gemini-1.5-flash",
        "Gemini 1.5 Pro (Reasoning - 150 RPM)": "gemini-1.5-pro",
        "Gemini 2.0 Pro Exp (Experimental)": "gemini-2.0-pro-exp-02-05"
    }
    # Default to Flash 2.0 for best performance
    selected_model_name = st.sidebar.selectbox("Select AI Model", list(model_options.keys()), index=0)
    selected_model_id = model_options[selected_model_name]

    # Upload Section
    uploaded_file = st.sidebar.file_uploader("Upload Audit Log (CSV, Excel, TXT, PDF)", type=["csv", "xlsx", "xls", "txt", "pdf"])

    if uploaded_file:
        try:
            # --- 1. Cloud Backup (Deduped) ---
            if 'uploaded_files' not in st.session_state:
                st.session_state['uploaded_files'] = []

            file_key = f"{user_email}_{uploaded_file.name}"
            
            # Only upload if not previously uploaded in this session
            if file_key not in st.session_state['uploaded_files']:
                file_content = uploaded_file.getvalue()
                with st.spinner("Encrypting & Backing up to Vault..."):
                     success, msg = cloud.upload_file(file_content, file_key)
                     if success:
                         st.toast("File securely loaded.")
                         st.session_state['uploaded_files'].append(file_key)
                     else:
                         if "already exists" in msg:
                             # Check if we should ignore existing files (e.g. re-upload same file)
                             st.session_state['uploaded_files'].append(file_key) # Mark as done to stop trying
                         else:
                             st.warning(f"Backup Warning: {msg}")
            
            # --- 2. Local Processing ---
            file_ext = uploaded_file.name.split('.')[-1].lower()
            data_content = None
            data_type = "unknown"

            # --- Optimized File Processing (Cache Parsing & PII) ---
            if 'processed_file' not in st.session_state or st.session_state.processed_file != uploaded_file.name:
                # 1. Parse File (Only if new)
                uploaded_file.seek(0)
                if file_ext == 'csv':
                    data_content = pd.read_csv(uploaded_file)
                    data_type = "dataframe"
                elif file_ext in ['xlsx', 'xls']:
                    data_content = pd.read_excel(uploaded_file)
                    data_type = "dataframe"
                elif file_ext == 'txt':
                    data_content = uploaded_file.read().decode("utf-8")
                    data_type = "text"
                elif file_ext == 'pdf':
                    import pypdf
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    data_content = text
                    data_type = "text"
                else:
                    data_content = None

                if data_content is not None:
                     # 2. Apply PII Masking
                    sec_engine = SecurityEngine()
                    with st.spinner(f"Processing & Applying PII Firewall to {file_ext.upper()}..."):
                        if data_type == "dataframe":
                            anonymized_content = sec_engine.anonymize_dataframe(data_content)
                        else:
                            anonymized_content = sec_engine.anonymize_text(data_content)
                    
                    # 3. Save to Cache
                    st.session_state.processed_file = uploaded_file.name
                    st.session_state.anonymized_content = anonymized_content
                    st.session_state.data_content = data_content
                    st.session_state.data_type = data_type
            
            else:
                # Retrieve from cache (Zero Latency)
                anonymized_content = st.session_state.anonymized_content
                data_content = st.session_state.data_content
                data_type = st.session_state.data_type

            # --- Data Preview ---
            if 'anonymized_content' in locals() and anonymized_content is not None:
                st.subheader("Data Inspector")
                view_mode = st.radio("View Mode:", ["Anonymized (Safe)", "Original (Risk)"], horizontal=True)
                
                if view_mode == "Original (Risk)":
                    st.warning("⚠️ Accessing raw data.")
                    if data_type == "dataframe":
                        st.dataframe(data_content.head(100))
                    else:
                        st.text_area("Raw Text", data_content, height=200)
                else:
                    st.success("✅ PII Masked.")
                    if data_type == "dataframe":
                        st.dataframe(anonymized_content.head(100))
                    else:
                        st.text_area("Anonymized Text", anonymized_content, height=200)

                # --- AI Analysis ---
                st.subheader("🤖 AI Security Analyst")
                ai_engine = AIEngine(model_id=selected_model_id)
                
                # Context Prep & Quota Management
                with st.expander("⚙️ Analysis Settings & Quota Code", expanded=False):
                    analysis_cap = st.slider("Max Rows/Chars to Analyze", min_value=10, max_value=1000, value=50, step=10, help="Higher values provide more context but use more API quota.")
                    st.caption(f"ℹ️ Estimated Token Usage: ~{analysis_cap * 20} tokens (Flash Model Cost: Very Low)")
                
                if data_type == "dataframe":
                    data_context = anonymized_content.head(analysis_cap).to_markdown(index=False)
                else:
                    data_context = anonymized_content[:analysis_cap * 100] # Approx chars

                if st.button("Run Full Security Audit"):
                    if not os.getenv("GEMINI_API_KEY"):
                        st.error("Missing API Key")
                    else:
                        with st.spinner("Analyzing (Phase 0: Sliding Window & Phase 4: JSON Output)..."):
                            result_text = ai_engine.analyze_log(data_context)
                            
                            # --- Phase 4: Structured Output Handling ---
                            import json
                            import re

                            try:
                                # Clean potential code blocks from response
                                clean_json = result_text.replace("```json", "").replace("```", "").strip()
                                audit_report = json.loads(clean_json)
                                
                                # 1. Executive Summary
                                st.subheader("📊 Audit Summary")
                                status_color = "red" if audit_report.get("compliance_status") == "NON_COMPLIANT" else "orange" if audit_report.get("compliance_status") == "WARNING" else "green"
                                st.markdown(f":{status_color}[**Status: {audit_report.get('compliance_status')}**]")
                                st.info(audit_report.get("executive_summary"))

                                # 2. Findings Table
                                st.subheader("🚩 Detected Findings")
                                findings = audit_report.get("findings", [])
                                if findings:
                                    df_findings = pd.DataFrame(findings)
                                    st.dataframe(df_findings, use_container_width=True)
                                else:
                                    st.success("No critical violations found.")

                                # 3. Recommendations
                                st.subheader("✅ Recommendations")
                                for rec in audit_report.get("recommendations", []):
                                    st.markdown(f"- {rec}")

                                # 4. Detailed Report (Markdown Style - User Preference)
                                st.divider()
                                st.subheader("📝 Detailed Audit Report")
                                
                                report_md = ""
                                for idx, finding in enumerate(findings, 1):
                                    report_md += f"### [Finding #{idx}] {finding.get('category')} ({finding.get('severity')})\n"
                                    report_md += f"**Description:**\n{finding.get('description')}\n\n"
                                    report_md += f"- **Evidence:** `{finding.get('evidence')}`\n"
                                    report_md += f"- **Regulation:** {finding.get('regulation')}\n\n"
                                    report_md += "---\n\n\n"
                                
                                st.markdown(report_md)

                                # Log to Cloud (JSON Summary)
                                cloud.log_chat(user_email, "Full Audit Request (JSON)", str(audit_report)[:500])

                            except json.JSONDecodeError:
                                st.warning("⚠️ Raw output returned (JSON Parsing Failed)")
                                st.markdown(result_text)
                                cloud.log_chat(user_email, "Full Audit Request (Raw)", result_text[:500])
                            
                user_query = st.text_input("Ask specific question (Chat Mode)")
                if st.button("Ask AI"):
                    if user_query and os.getenv("GEMINI_API_KEY"):
                            with st.spinner("Consulting..."):
                                answer = ai_engine.analyze_log(data_context, user_query=user_query)
                                st.markdown(f"**A:** {answer}")
                                # Log to Cloud
                                cloud.log_chat(user_email, user_query, answer)

        except Exception as e:
            st.error(f"Error: {e}")

def main():
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    auth = AuthManager()
    
    if st.session_state['user']:
        main_app(st.session_state['user'])
    else:
        login_page(auth)

if __name__ == "__main__":
    main()
