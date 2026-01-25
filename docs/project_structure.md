# AI-Audit-Reviewer 프로젝트 구조

이 문서는 **AI-Audit-Reviewer (Phase 1)**의 권장 파일 및 폴더 구조를 설명합니다. 이 구조는 보안 로직, 비즈니스 로직, UI를 명확히 분리하여 모듈성을 높이도록 설계되었습니다.

## 디렉토리 트리 (Directory Tree)

```
AI-Audit-Reviewer/
├── .env                  # [보안] 환경 변수 (API 키 등). 절대 Git에 커밋하지 마세요!
├── .gitignore            # Git 제외 설정 (.env, venv/, __pycache__/ 제외)
├── requirements.txt      # 파이썬 의존성 목록 (streamlit, google-genai, presidio 등)
├── README.md             # 프로젝트 문서 및 설치 가이드
├── app.py                # [UI] Streamlit 애플리케이션의 메인 실행 파일
├── security_utils.py     # [Core] PII 마스킹 및 보안 로직 ("PII 방화벽" 역할)
├── ai_utils.py           # [Core] Google Gemini 3.0 API 연동 로직
└── tests/                # [품질] 자동화 테스트 폴더
    └── test_security.py  # PII 마스킹이 정상 작동하는지 확인하는 단위 테스트
```

## 상세 설명

### 핵심 모듈 (Core Modules)
*   **`app.py`**: "프론트엔드" 역할입니다. 사용자 입력을 받고, 파일을 업로드하고, 결과를 보여줍니다. 복잡한 로직은 직접 처리하지 않고 `security_utils`와 `ai_utils`를 호출합니다.
*   **`security_utils.py`**: "문지기(Gatekeeper)" 역할입니다. `SecurityEngine` 클래스가 여기에 있습니다. 원본 데이터는 이 모듈을 통과하여 익명화되지 않고서는 밖으로 나갈 수 없습니다. `presidio-analyzer`와 `presidio-anonymizer`를 사용합니다.
*   **`ai_utils.py`**: "두뇌(Brain)" 역할입니다. `AIEngine` 클래스가 있습니다. Google Gemini 3.0과의 연결을 관리하고, 프롬프트를 구성하며, AI의 응답을 처리합니다.

### 설정 (Configuration)
*   **`.env`**: `GEMINI_API_KEY`와 같은 민감한 정보를 저장합니다.
    *   예시: `GEMINI_API_KEY=AIzaSy...`

### 테스트 (Testing)
*   **`tests/`**: 테스트 스크립트를 모아두는 폴더입니다.
    *   **`test_security.py`**: 규정 준수를 위해 가장 중요합니다. 배포 전에 "김철수" 같은 이름이 실제로 `<PERSON>`으로 변환되는지 기계적으로 검증합니다.

## 추천 작업 흐름 (Recommended Workflow)
1.  **설치**: `pip install -r requirements.txt`
2.  **설정**: `python -m spacy download en_core_web_lg` (정확한 PII 탐지를 위해 필수)
3.  **실행**: `streamlit run app.py`
