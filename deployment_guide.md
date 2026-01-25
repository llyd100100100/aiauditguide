# AI-Audit-Reviewer 배포 가이드 (Cloud Native)

**Streamlit Cloud**를 이용하여 어디서나 접속 가능한 웹 앱을 만들면서, 데이터는 **Google Drive/Sheets**에 안전하게 저장하는 하이브리드 전략입니다.

---

## 🚀 메인 전략: Streamlit Cloud + Google Workspace
*앱은 클라우드에 있지만, 파일과 로그는 내 구글 드라이브와 시트에 저장됩니다.*

### 0. 준비물
1.  **Google Cloud Service Account 키** (문서 참고: `docs/service_account_setup.md`)
2.  **GitHub 계정**

### 1. GitHub 업로드
1.  이 프로젝트 폴더 전체를 GitHub 리포지토리에 올립니다.
    *   주의: `.env`나 `secrets.toml`, 키 파일 등은 절대 올리지 마세요 (`.gitignore`에 의해 자동 제외됨).

### 2. Streamlit Cloud 설정
1.  [share.streamlit.io](https://share.streamlit.io) 접속 및 로그인.
2.  `New app` -> 리포지토리 선택 -> Main file path: `app.py`.
3.  **Advanced settings** -> **Secrets** 클릭.
4.  다음 내용을 입력합니다 (Service Account JSON 내용을 TOML 형식으로 변환):

    ```toml
    GEMINI_API_KEY = "..."

    [gcp_service_account]
    type = "service_account"
    project_id = "..."
    # ... (JSON 파일 내용 복사) ...

    gcp_drive_folder_id = "구글드라이브_폴더ID"
    gcp_user_sheet_name = "Audit_Users"
    gcp_sheet_name = "Audit_Logs"
    ```
5.  **Deploy** 버튼 클릭!

### 3. 관리자 확인 방법
*   **파일 확인**: 내 **Google Drive**의 지정된 폴더(`Audit_Vault`)에 접속하면 사용자가 업로드한 파일들이 쌓여 있습니다.
*   **로그 확인**: 내 **Google Sheets**(`Audit_Logs`)를 열면 누가 언제 무엇을 물어봤는지 엑셀처럼 볼 수 있습니다.

---

## 🔒 대안: Docker (사내 폐쇄망용)
*인터넷이 안 되는 환경이나, 구글 드라이브를 쓸 수 없는 경우 사용합니다.*

1.  **빌드**: `docker build -t ai-audit-reviewer .`
2.  **실행**: `docker run -p 8501:8501 ai-audit-reviewer`
    *   이 경우 데이터는 컨테이너 내부에만 존재하므로, 영구 저장을 위해선 `-v /host/path:/app/data` 옵션이 필요합니다.
