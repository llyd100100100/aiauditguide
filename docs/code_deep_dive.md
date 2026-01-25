# AI Audit Reviewer - 상세 코드 분석 (Code Walkthrough)

이 문서는 프로젝트의 핵심 기능인 **1) 오딧 파일 파싱**과 **2) AI 분석 요청** 부분이 실제 코드로 어떻게 구현되어 있는지 상세하게 설명합니다.

---

## 1. 오딧 로그 파일 파싱 (Log Parsing Logic)
**파일 위치**: [`app.py`](../app.py)

사용자가 업로드한 파일의 확장자(Format)를 자동으로 인식하여, AI가 이해할 수 있는 형태(텍스트 또는 표)로 변환하는 과정입니다.

```python
# app.py 의 실제 파일 처리 로직
file_ext = uploaded_file.name.split('.')[-1].lower() # 1. 확장자 추출

# 변수 초기화
data_content = None 
data_type = "unknown"

# 2. 확장자별 분기 처리 (Universal Parsing)
if file_ext == 'csv':
    # CSV는 Pandas로 읽어서 데이터프레임(표)으로 만듭니다.
    data_content = pd.read_csv(uploaded_file)
    data_type = "dataframe"

elif file_ext in ['xlsx', 'xls']:
    # 엑셀도 Pandas로 읽습니다. 시트가 여러 개여도 첫 번째 시트를 읽습니다.
    data_content = pd.read_excel(uploaded_file)
    data_type = "dataframe"

elif file_ext == 'txt':
    # 텍스트 파일은 바이트(Byte)로 읽히므로 utf-8로 디코딩하여 문자열로 만듭니다.
    data_content = uploaded_file.read().decode("utf-8")
    data_type = "text"

elif file_ext == 'pdf':
    # PDF는 'pypdf' 라이브러리를 사용합니다.
    import pypdf
    pdf_reader = pypdf.PdfReader(uploaded_file)
    text = ""
    # 모든 페이지를 돌면서 글자를 추출하여 하나의 긴 텍스트로 합칩니다.
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    data_content = text
    data_type = "text"
```

**💡 핵심 포인트:**
- **확장성**: `if/elif` 구조로 되어 있어 새로운 파일 포맷(예: xml, json)이 생기면 이 부분만 추가하면 됩니다.
- **정형/비정형 구분**: `dataframe` (표) 타입과 `text` (줄글) 타입을 구분하여, 나중에 필터링 로직을 다르게 적용합니다.

---

## 2. AI 분석 및 재시도 로직 (AI Integration & Retry)
**파일 위치**: [`ai_utils.py`](../ai_utils.py)

구글 Gemini에게 데이터를 보내고 답변을 받는 부분입니다. 특히 API 사용량 제한(429 Error)을 극복하기 위한 재시도 로직이 핵심입니다.

### 2.1 자동 재시도 장치 (Auto-Retry Decorator)
```python
# ai_utils.py 의 재시도 설정
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# 이 함수는 실패하면 자동으로 재실행됩니다.
@retry(
    # 'ResourceExhausted' (쿼터 초과) 에러가 날 때만 재시도합니다.
    retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
    
    # 최대 7번까지 시도합니다. (끈질기게!)
    stop=stop_after_attempt(7),
    
    # 대기 시간: 처음엔 5초, 그 다음엔 10초, 20초... 최대 60초까지 늘려가며 기다립니다.
    wait=wait_exponential(multiplier=2, min=5, max=60)
)
def _generate_content_with_retry(self, prompt, context):
    # 실제 Google API 호출 부분
    return self.client.models.generate_content(
        model=self.model_id,
        contents=[prompt, context],
        config=types.GenerateContentConfig(temperature=0.1) # 0.1: 창의성보다는 팩트 위주 답변
    )
```

### 2.2 프롬프트 구성 및 요청 (Prompting)
```python
def analyze_log(self, anonymized_text: str, user_query: str = "") -> str:
    # ... (API 키 확인 생략) ...

    # AI에게 역할을 부여하는 기본 지시문 (System Instruction 역할)
    default_instruction = """
    You are an expert Security Audit Log Analyst.
    Input Data: ... (데이터 설명) ...
    Your Goal: ... (분석 목표: 삭제, 비인가 접근 등 찾기) ...
    """
    
    # 사용자가 질문을 했으면 질문을 포함하고, 아니면 요약을 요청
    if user_query:
        prompt = f"{default_instruction}\n\nUSER QUESTION: {user_query}\n..."
    else:
        prompt = f"{default_instruction}\n\nPerform a comprehensive security audit summary."

    try:
        # 위에서 정의한 '재시도 함수'를 통해 안전하게 요청
        response = self._generate_content_with_retry(prompt, anonymized_text)
        return response.text
    except Exception as e:
        # 7번 다 실패하면 에러 로그를 남깁니다.
        logger.error(f"AI Analysis failed: {e}")
        return f"Error during AI analysis: {str(e)}"
```

**💡 핵심 포인트:**
- **회복 탄력성(Resilience)**: `@retry` 데코레이터 덕분에 네트워크가 불안하거나 사용량이 몰려도 에러 없이 결과를 받아낼 확률이 매우 높습니다.
- **컨텍스트 분리**: 시스템 지시문(`default_instruction`)과 사용자 질문(`user_query`), 그리고 실제 데이터(`anonymized_text`)를 명확히 구분하여 AI가 혼동하지 않도록 설계했습니다.
