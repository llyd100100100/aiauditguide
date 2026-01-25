# AI-Audit-Reviewer (Phase 1 Prototype)

AI-Audit-Reviewer는 감사를 위한 로그 분석 자동화 도구입니다. 개인정보(PII)를 자동으로 마스킹한 후 Google Gemini 3.0을 사용하여 보안 위협을 분석합니다.

## 설치 및 실행

1.  **가상 환경 생성 및 활성화**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **의존성 설치**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Spacy 모델 다운로드 (PII 탐지용)**
    ```bash
    python -m spacy download en_core_web_lg
    ```

4.  **환경 변수 설정**
    `.env` 파일을 생성하고 API 키를 입력하세요 (선택 사항, UI에서도 입력 가능).
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

5.  **실행**
    ```bash
    streamlit run app.py
    ```

## 테스트
```bash
pytest tests/
```
