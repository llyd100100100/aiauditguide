import streamlit as st
from supabase import create_client, Client
import datetime

class CloudManager:
    def __init__(self):
        # Initialize Supabase
        self.supabase: Client = None
        sb_url = st.secrets.get("SUPABASE_URL")
        sb_key = st.secrets.get("SUPABASE_KEY")
        
        self.is_connected = False
        if sb_url and sb_key:
            try:
                self.supabase = create_client(sb_url, sb_key)
                self.is_connected = True
            except Exception as e:
                print(f"Supabase Init Error: {e}")

    def upload_file(self, file_content: bytes, filename: str) -> tuple[bool, str]:
        """Uploads a file to Supabase Storage bucket 'audit-vault'."""
        if not self.is_connected:
            return False, "Supabase Configuration Missing."

        try:
            # Bucket name must be 'audit-vault' (User created)
            bucket_name = "audit-vault"
            
            # Avoid duplicate overwrite errors by adding timestamp if needed, 
            # though generic upload usually handles or fails. 
            # Supabase storage 'upload' fails if file exists. We might use 'upsert' option if available in py lib 
            # or just let it fail and rename. Let's try upsert logic or simple upload.
            
            # Note: storage.from_() returns a StorageFileApi
            res = self.supabase.storage.from_(bucket_name).upload(
                path=filename,
                file=file_content,
                file_options={"content-type": "application/octet-stream", "upsert": "false"} 
            )
            # res usually returns path or id
            return True, f"Uploaded to {bucket_name}/{filename}"
            
        except Exception as e:
            # Common error: 'The resource already exists'. Attempt rename or specific check?
            # For this MVP, we just return the error.
            if "already exists" in str(e):
                return False, "File already exists in Vault."
            return False, f"Storage Error: {str(e)}"

    def log_chat(self, user_name: str, question: str, answer: str) -> tuple[bool, str]:
        """Logs chat to Supabase 'chat_logs' table."""
        if not self.is_connected:
            return False, "Supabase Configuration Missing."

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
            return False, f"Log Error: {str(e)}"
