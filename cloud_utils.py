import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from supabase import create_client, Client
import io
import datetime

# Scopes required for Drive (Sheets scope removed if not used, but keeping for compatibility)
SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

class CloudManager:
    def __init__(self):
        # 1. Google Drive Init
        self.creds = self._get_credentials()
        self.drive_connected = self.creds is not None
        
        # 2. Supabase Init
        self.supabase: Client = None
        sb_url = st.secrets.get("SUPABASE_URL")
        sb_key = st.secrets.get("SUPABASE_KEY")
        if sb_url and sb_key:
            self.supabase = create_client(sb_url, sb_key)

    def _get_credentials(self):
        """Loads GCP credentials from Streamlit secrets."""
        if "gcp_service_account" not in st.secrets:
            return None
        return Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=SCOPES
        )

    def upload_file(self, file_content: bytes, filename: str, folder_id: str = None) -> tuple[bool, str]:
        """Uploads a file to Google Drive."""
        if not self.drive_connected:
            return False, "Google Drive not configured."

        try:
            if not folder_id:
                folder_id = st.secrets.get("gcp_drive_folder_id")

            service = build('drive', 'v3', credentials=self.creds)
            file_metadata = {'name': filename}
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='application/octet-stream', resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return True, file.get('id')
            
        except Exception as e:
            return False, f"Drive Upload Error: {str(e)}"

    def log_chat(self, user_name: str, question: str, answer: str) -> tuple[bool, str]:
        """Logs chat to Supabase 'chat_logs' table."""
        if not self.supabase:
            return False, "Supabase not configured."

        try:
            data = {
                "user_name": user_name,
                "question": question,
                "answer": answer,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.supabase.table("chat_logs").insert(data).execute()
            return True, "Log saved to Supabase"
            
        except Exception as e:
            return False, f"Supabase Log Error: {str(e)}"
