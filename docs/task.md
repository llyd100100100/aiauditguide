# 프로젝트 분석 및 계획

- [x] 대화 로그 분석 <!-- id: 0 -->
    - [x] 모든 "새 텍스트 문서*.txt" 파일 읽기 <!-- id: 1 -->
    - [x] 요구사항 종합 <!-- id: 2 -->
- [x] 프로젝트 요약 문서 작성 (한글 변환) <!-- id: 3 -->
- [x] 구현 계획서 작성 (한글 변환) <!-- id: 4 -->
- [x] 프로젝트 구조 설명서 작성 (한글 변환) <!-- id: 5 -->

# Phase 1 Implementation
- [x] Initialize Project Environment <!-- id: 6 -->
    - [x] Create .gitignore <!-- id: 7 -->
    - [x] Create requirements.txt <!-- id: 8 -->
    - [x] Create README.md <!-- id: 9 -->
- [x] Implement Security Module <!-- id: 10 -->
    - [x] Create security_utils.py <!-- id: 11 -->
    - [x] Create tests/test_security.py <!-- id: 12 -->
- [x] Implement AI Module <!-- id: 13 -->
    - [x] Create ai_utils.py <!-- id: 14 -->
- [x] Implement User Interface <!-- id: 15 -->
    - [x] Create app.py <!-- id: 16 -->
- [x] Verify Implementation <!-- id: 17 -->
    - [x] Run security tests <!-- id: 18 -->
    - [x] Manual walkthrough <!-- id: 19 -->

# Refinement (Based on Feedback)
- [x] Update Implementation Plan <!-- id: 23 -->
- [x] Enhance UI (app.py) <!-- id: 24 -->
    - [x] Add Custom Query Input <!-- id: 25 -->
    - [x] Add Filter Options (User, Action) <!-- id: 26 -->
    - [x] Auto-load API Key from .env <!-- id: 27 -->
- [x] Update AI Logic (ai_utils.py) <!-- id: 28 -->
- [x] Create Test Data (dummy_audit_log.csv) <!-- id: 29 -->
- [x] Implement API Retry Logic (429 Fix) <!-- id: 29-1 -->

# Phase 2: Expanded Format Support
- [x] Create Diverse Test Data <!-- id: 30 -->
    - [x] Create test_data folder <!-- id: 31 -->
    - [x] Generate GMP QC CSV (HPLC) <!-- id: 32 -->
    - [x] Generate Production Excel (Batch) <!-- id: 33 -->
    - [x] Generate Lab PDF (Balance) <!-- id: 34 -->
- [x] Implement PDF & Text Support <!-- id: 35 -->
    - [x] Update requirements.txt (pypdf) <!-- id: 36 -->
    - [x] Update app.py for PDF parsing <!-- id: 37 -->

# Optimization & Refinement (Current)
- [x] Implement Session State Caching (Fix PII re-run) <!-- id: 38 -->
- [x] Add Model Selection Dropdown <!-- id: 39 -->
- [x] Add Token Usage/Quota Visualization <!-- id: 39-1 -->
- [x] Optimize AI System Prompt (Audit Compliance) <!-- id: 39-2 -->
    - [x] Phase 0: Sliding Window Algorithm (Chunking & Overlap) <!-- id: 39-3 -->
    - [x] Phase 1: Persona & Chain-of-Thought (CoT) <!-- id: 39-4 -->
    - [x] Phase 2: Modular Few-Shot Examples (Examples Lib) <!-- id: 39-5 -->
    - [x] Phase 3: Grounding (Citation Rules) <!-- id: 39-6 -->
    - [x] Phase 4: Structured Output (JSON Schema) <!-- id: 39-7 -->
    - [x] Phase 5: Expert Optimization (Based on Code Review) <!-- id: 39-8 -->
        - [x] Implement Sliding Window with Overlap (2000 chars) <!-- id: 39-9 -->
        - [x] Implement Safe JSON Parsing & Deduplication <!-- id: 39-10 -->
        - [x] Implement Deterministic Verification Loop (Evidence Check) <!-- id: 39-11 -->
        - [x] Enhance CoT Prompt (Action Analysis & English-Korean Flow) <!-- id: 39-12 -->
    - [x] Phase 6: Advanced PII Masking (Context-Preserving) <!-- id: 39-13 -->
        - [x] Implement Deterministic Pseudonymization (HMAC-SHA256) <!-- id: 39-14 -->
        - [x] Update security_utils.py to use Hash Mapping instead of generic tags <!-- id: 39-15 -->

# Deployment
- [x] Prepare Deployment Artifacts <!-- id: 20 -->
    - [x] Create Dockerfile <!-- id: 21 -->
    - [x] Create deployment_guide.md <!-- id: 22 -->

# Phase 2: Structural Learning (RAG) & Visualization
- [ ] Implement Knowledge Base (RAG) <!-- id: 40 -->
    - [ ] Install dependencies (langchain, chromadb, plotly) <!-- id: 41 -->
    - [ ] Create knowledge_base.py (Vector DB logic) <!-- id: 42 -->
    - [ ] Implement PDF Ingestion & Chunking <!-- id: 43 -->
- [ ] Update AI Engine <!-- id: 44 -->
    - [ ] Integrate Context Retrieval into ai_utils.py <!-- id: 45 -->
    - [ ] Update System Prompt for RAG <!-- id: 46 -->
- [ ] Update User Interface <!-- id: 47 -->
    - [ ] Add SOP Upload Section to Sidebar <!-- id: 48 -->
    - [ ] Implement Interactive Charts (Plotly) <!-- id: 49 -->
