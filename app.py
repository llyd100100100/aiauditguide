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

    st.title("🛡️ AI-Audit-Reviewer (Cloud Native)")
    st.markdown("""
    **Secure Audit Log Analysis** utilizing Google Gemini Flash.
    
    - **Raw Files**: Auto-backed up to secure **Admin Vault** (Supabase Storage).
    - **Audit Trail**: All Q&A is logged to **Supabase Audit DB**.
    
    *Enterprise-grade security for your audit logs.*
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

    # Upload Section
    uploaded_file = st.sidebar.file_uploader("Upload Audit Log (CSV, Excel, TXT, PDF)", type=["csv", "xlsx", "xls", "txt", "pdf"])

    if uploaded_file:
        try:
            # --- 1. Cloud Backup (Immediate) ---
            file_content = uploaded_file.getvalue()
            # Only upload if not already done for this session/file (Optional optimization)
            with st.spinner("Encrypting & Backing up to Vault..."):
                 success, msg = cloud.upload_file(file_content, f"{user_email}_{uploaded_file.name}")
                 if success:
                     st.toast(f"File backed up to Vault (ID: {msg[-6:]}...)")
                 else:
                     st.warning(f"Backup Warning: {msg}")

            # --- 2. Local Processing ---
            file_ext = uploaded_file.name.split('.')[-1].lower()
            data_content = None
            data_type = "unknown"

            # Parse
            uploaded_file.seek(0) # Reset pointer
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
            
            if data_content is not None:
                # --- Security Phase ---
                sec_engine = SecurityEngine()
                anonymized_content = None

                with st.spinner(f"Applying PII Firewall..."):
                    if data_type == "dataframe":
                        anonymized_content = sec_engine.anonymize_dataframe(data_content)
                    else:
                        anonymized_content = sec_engine.anonymize_text(data_content)

                # --- Data Preview ---
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
                ai_engine = AIEngine()
                
                # Context Prep
                if data_type == "dataframe":
                    data_context = anonymized_content.head(50).to_markdown(index=False)
                else:
                    data_context = anonymized_content[:5000]

                if st.button("Run Full Security Audit"):
                    if not os.getenv("GEMINI_API_KEY"):
                        st.error("Missing API Key")
                    else:
                        with st.spinner("Analyzing..."):
                            result = ai_engine.analyze_log(data_context)
                            st.markdown(result)
                            # Log to Cloud
                            cloud.log_chat(user_email, "Full Audit Request", result[:500] + "...")

                user_query = st.text_input("Ask specific question")
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
