import streamlit as st
from cloud_utils import CloudManager
import time

class AuthManager:
    def __init__(self):
        self.cloud = CloudManager() # This initializes Supabase client

    def register_user(self, email, password, name):
        """Registers a user using Supabase Auth."""
        if not self.cloud.supabase:
            return False, "Supabase credentials missing"

        try:
            # 1. Sign Up in Auth
            response = self.cloud.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"full_name": name}
                }
            })
            
            # Check if user object exists in response
            if response.user:
                return True, "Registration successful! Please check email for confirmation (if enabled) or login."
            else:
                return False, "Registration failed (No user returned)"
                
        except Exception as e:
            return False, f"Registration Error: {str(e)}"

    def login_user(self, email, password):
        """Logs in using Supabase Auth."""
        if not self.cloud.supabase:
            # Fallback for unconnected local test
            if email == "admin" and password == "admin":
                 return True, {"email": "admin", "user_metadata": {"full_name": "Local Admin"}}
            return False, "Supabase credentials missing"

        try:
            response = self.cloud.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                return True, response.user
            else:
                return False, "Login failed"
        except Exception as e:
             return False, f"Login Error: {str(e)}"
