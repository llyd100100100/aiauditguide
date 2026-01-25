# AI-Audit-Reviewer 구현 계획 (Phase 1)

**목표**: Google Gemini 3.0을 활용하여 감사 로그를 분석하는 안전한 AI 프로토타입을 구축합니다. Microsoft Presidio를 이용한 강력한 "PII 방화벽"이 핵심입니다.

## 사용자 검토 필요 (User Review Required)
> [!IMPORTANT]
> **API 비용**: 이 프로토타입은 Google Gemini 3.0 API를 사용합니다. 결제가 활성화된 유효한 API 키가 있는지 확인해 주세요.
> **보안 주의**: 개인정보는 마스킹되지만, **국가 기밀 등 극도로 민감한 데이터**는 이 웹 기반 프로토타입에 업로드하지 마십시오.

## 제안된 변경 사항 (Proposed Changes)

### 환경 및 설정 (Environment & Setup)
#### [NEW] [requirements.txt](file:///requirements.txt)
- 의존성 패키지 정의: `streamlit`, `pandas`, `google-genai`, `presidio-analyzer`, `presidio-anonymizer`, `spacy`, `python-dotenv`.
- **참고**: Spacy의 `en_core_web_lg` 모델(정확한 PII 탐지용)을 다운로드하는 스크립트가 필요합니다.

### 핵심 모듈 (Core)
#### [NEW] [security_utils.py](file:///security_utils.py)
- **`SecurityEngine` 클래스**:
    - `Presidio Analyzer`와 `Anonymizer`를 효율적으로 관리(싱글톤 패턴).
    - `anonymize_text(text)`: 이름, IP, 이메일 등을 `<PERSON>`, `<IP_ADDRESS>`와 같은 태그로 변환.
    - `anonymize_dataframe(df)`: 대용량 처리 속드를 위해 문자열 컬럼만 선택적으로 검사.

#### [NEW] [ai_utils.py](file:///ai_utils.py)
- **`AIEngine` 클래스**:
    - `google-genai` SDK 래퍼(Wrapper).
    - `analyze_log(anonymized_data)`: 익명화된 데이터를 Gemini 3.0에 전송.
    - **프롬프트 엔지니어링**: 시스템 프롬프트에 `<TAGS>`를 데이터 변수로 인식하고 이상 징후 탐지에 집중하도록 지시.
    - **설정**: `temperature=0.1`로 설정하여 일관되고 논리적인 분석 결과 유도.

### 사용자 인터페이스 (Interface)
#### [NEW] [app.py](file:///app.py)
- **메인 Streamlit 애플리케이션**:
    - **사이드바**: 파일 업로더(CSV/Excel), API 키 입력창.
    - **메인 화면**:
        - 데이터 미리보기 (원본 vs 익명화 데이터 토글 기능).
        - "분석 시작(Analyze)" 버튼.
        - 결과 화면 (마크다운 리포트 + JSON 요약).

## 검증 계획 (Verification Plan)

### 자동화 테스트 (Automated Tests)
- **보안 단위 테스트**: `tests/test_security.py`를 작성하여 `SecurityEngine`이 실제 이름("홍길동")과 IP("192.168.1.1")를 정확히 마스킹하는지 검증합니다.
    - 실행 명령어: `pytest tests/test_security.py`

### 수동 검증 (Manual Verification)
1.  **앱 실행**: `streamlit run app.py` 명령어로 실행.
2.  **샘플 업로드**: 가짜 이름과 IP가 포함된 테스트용 감사 로그 업로드.
3.  **마스킹 확인**: UI에서 "익명화 데이터 보기"를 켜서 이름/IP가 태그로 가려졌는지 눈으로 확인.
4.  **분석 확인**: "분석 시작" 버튼을 누르고 Gemini가 로그의 라인 번호를 인용하며 분석 결과를 내놓는지 확인.
