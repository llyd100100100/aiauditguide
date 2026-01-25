# 🛠️ AI-Audit-Reviewer 완전 설정 가이드

이 문서는 **앱을 인터넷에 배포(Streamlit Cloud)** 하고, **로그인/DB(Supabase)** 와 **파일 저장(Google Drive)** 을 연결하는 모든 과정을 다룹니다.

---

## 1단계: Supabase 설정 (로그인 & DB)
*사용자의 이메일 로그인 정보와 채팅 내용을 저장하는 곳입니다.*

1.  [Supabase.com](https://supabase.com) 접속 및 **Start your project** 클릭 (GitHub 아이디로 로그인).
2.  **New Project** 클릭 -> Organization 선택 -> 이름 입력 (예: `audit-bot`) -> DB 비밀번호 설정(기억해두세요/생성버튼 클릭) -> **Create new project**.
3.  **API Key 확인**:
    *   프로젝트 대시보드 왼쪽 메뉴 맨 아래 **Project Settings (톱니바퀴) ⚙️** -> **API**.
    *   `Project URL`과 `Project API keys (anon public)` 두 가지 값을 복사해서 메모장에 둡니다. (나중에 씀)
4.  **Database 테이블 생성**:
    *   왼쪽 메뉴 **Table Editor** (표 아이콘) -> **Create a new table**.
    *   Name: `chat_logs` (대소문자 정확히).
    *   Columns 추가:
        *   `id` (int8, Primary Key) - 기본값 유지
        *   `user_name` (text)
        *   `question` (text)
        *   `answer` (text)
        *   `timestamp` (text 또는 timestamptz)
    *   **Save** 클릭.
    
CREATE TABLE chat_logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_name TEXT,
    question TEXT,
    answer TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW() -- 시간 자동 기록
);
-- 2. 보안 정책 (RLS) 설정: 권한 문제 방지
ALTER TABLE chat_logs ENABLE ROW LEVEL SECURITY;
-- (중요) 앱에서 데이터를 넣고 볼 수 있게 모든 권한 허용
CREATE POLICY "Enable access for all users" ON chat_logs
FOR ALL USING (true) WITH CHECK (true);
---

## 2단계: Google Cloud 설정 (파일 저장소)
*사용자가 올린 파일을 내 구글 드라이브에 자동으로 저장하기 위한 키입니다.*

1.  [Google Cloud Console](https://console.cloud.google.com/) 접속.
2.  **프로젝트 생성**: 상단 프로젝트 선택 -> **새 프로젝트** -> 이름 입력 -> 만들기.
3.  **API 사용 설정**:
    *   상단 검색창에 `Google Drive API` 검색 -> **사용(Enable)** 클릭.
4.  **서비스 계정(Service Account) 만들기**:
    *   검색창에 `서비스 계정` 검색 -> **IAM 및 관리자** > **서비스 계정**.
    *   **+ 서비스 계정 만들기** 클릭 -> 이름 입력(예: `audit-uploader`) -> 완료.
    *   생성된 이메일 주소(`audit-uploader@...`)를 **복사**.




5.  **키(JSON) 다운로드**:
    *   방금 만든 계정 클릭 -> 상단 **키** 탭 -> **키 추가** -> **새 키 만들기** -> **JSON** 선택 -> 만들기.
    *   파일이 다운로드됩니다. (‼️ 절대 남에게 주지 마세요)



6.  **Google Drive 폴더 공유**:
    *   내 구글 드라이브에 접속 -> 백업용 폴더 생성(예: `Audit_Vault`).
    *   폴더 우클릭 -> **공유** -> 방금 복사한 서비스 계정 이메일(`audit-uploader@...`) 붙여넣기 -> **편집자** 권한 부여 -> 전송.
    *   **폴더 ID 복사**: 폴더에 들어갔을 때 주소창의 마지막 부분 (`drive.google.com/drive/folders/이부분이_ID입니다`) 복사.

---

## 3단계: Streamlit Cloud 배포 (최종)
*여기에 위에서 얻은 키들을 입력하면 앱이 작동합니다.*

1.  [Streamlit Cloud](https://share.streamlit.io/) 접속 (GitHub 로그인).
2.  **New app** 클릭 -> `Paste GitHub URL` 선택.
3.  아까 업로드한 GitHub 주소 입력: `https://github.com/llyd100100100/aiauditguide`.
4.  **Advanced settings** 클릭 (배포 버튼 누르기 전 필수!).
5.  **Secrets** 입력창에 아래 내용을 빈칸을 채워서 붙여넣습니다:

```toml
# 1. 구글 Gemini 키
GEMINI_API_KEY = "여기에_Gemini_API_Key_입력"

# 2. Supabase 키 (1단계에서 복사한 것)
SUPABASE_URL = "여기에_Project_URL_입력"
SUPABASE_KEY = "여기에_anon_public_key_입력"

# 3. 구글 서비스 계정 키 (2단계 JSON 파일 내용을 복사해서 아래 형식에 맞게 채움)
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."

# 4. 구글 드라이브 폴더 ID (2단계 마지막에 복사한 것)
gcp_drive_folder_id = "여기에_폴더ID_입력"
```

6.  **Deploy!** 버튼 클릭.
7.  약 2~3분 뒤 "Your app is ready!"와 함께 앱이 뜹니다.

---
**팁**: JSON 파일 내용을 Secrets 형식으로 바꾸는 게 어렵다면, JSON 파일 전체 내용을 복사해서 저에게 보여주시면(보안 주의) 변환해 드릴 수도 있습니다. 하지만 직접 하시는 게 가장 안전합니다.
