# Google Cloud Service Account Setup Guide

To enable **Cloud Backup (Google Drive)** and **Audit Logging (Google Sheets)**, you need a Service Account Key.

## 1. Create Project & Enable APIs
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a **New Project** (e.g., `audit-reviewer-app`).
3.  Search for and **Enable** the following APIs:
    *   **Google Drive API**
    *   **Google Sheets API**

## 2. Create Service Account
1.  Go to **IAM & Admin** > **Service Accounts**.
2.  Click **Create Service Account**.
3.  Name: `audit-bot`.
4.  **Grant Access**: Select logic like `Editor` (or specifically Drive/Sheets Editor).
5.  Click **Done**.

## 3. Generate JSON Key
1.  Click on the newly created Service Account email (e.g., `audit-bot@...`).
2.  Go to **Keys** tab > **Add Key** > **Create new key** > **JSON**.
3.  A file will download. **Keep this safe!**

## 4. Setup Google Drive & Sheets
1.  **Drive**: Create a folder in your Google Drive (e.g., `Audit_Vault`).
    *   **Share** this folder with the **Service Account Email** (Editor or Contributor access).
    *   Copy the **Folder ID** from the URL (the random string at the end).
2.  **Sheets**: Create a new Sheet (e.g., `Audit_Logs`).
    *   **Share** this sheet with the **Service Account Email**.
    *   **Rename** the sheet tab to `Sheet1` (default).

## 5. Configure Streamlit Secrets
**For Local Run**:
Create `.streamlit/secrets.toml` in your project folder:

```toml
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "..."
token_uri = "..."
auth_provider_x509_cert_url = "..."
client_x509_cert_url = "..."

gcp_drive_folder_id = "YOUR_FOLDER_ID_HERE"
gcp_user_sheet_name = "Audit_Users"
gcp_sheet_name = "Audit_Logs" 
```
*(Copy values from your JSON key)*

**For Streamlit Cloud**:
1.  Go to App Settings > **Secrets**.
2.  Paste the TOML content above.
