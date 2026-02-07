# AI-Audit-Reviewer Implementation Plan (Phase 2: Structural Learning - RAG & Visualization)

**Goal**: Elevate the tool from a "Log Analyzer" to a "Context-Aware Auditor". We will implement **RAG (Retrieval-Augmented Generation)** to allow the AI to reference company SOPs (Standard Operating Procedures) when finding anomalies. We will also add **Interactive Visualizations** to spot trends.

### Phase 4: Structured Output (Completed)
- Define robust JSON schema for findings.
- Ensure strict separation of English and Korean outputs.

### Phase 5: Expert Optimization (Completed)
- Implement Sliding Window with Overlap (2000 chars) to prevent context loss.
- Implement Safe JSON Parsing & Deduplication logic.
- add **Deterministic Verification Loop** to cross-check AI findings against raw logs.
- Enhance CoT prompts for deeper analysis.

### Phase 6: Advanced PII Masking (Completed)
- Implement **Context-Preserving Pseudonymization** using HMAC-SHA256.
- Replace generic tags (`<PERSON>`) with consistent hashes (`<User_a1b2c>`).
- Ensure referential integrity across multiple logs effectively.

## User Review Required
> [!IMPORTANT]
> **New Dependencies**: We will add `langchain`, `chromadb` (Vector DB), and `plotly`.
> **Performance**: RAG requires embedding documents. Initial processing of large SOP PDFs might take a few seconds.

## Proposed Changes

### 1. Knowledge Base (RAG) Module
#### [NEW] [knowledge_base.py](file:///knowledge_base.py)
*   **`KnowledgeBase` Class**:
    *   **Ingestion**: Logic to read PDF/TXT SOP files.
    *   **Chunking**: Split documents into manageable chunks (e.g., 500 characters) with overlap.
    *   **Vector Store**: Use a local Vector DB (ChromaDB or FAISS) to store embeddings.
    *   **Retrieval**: `search_context(query)` method to find SOP sections relevant to a specific log entry.

### 2. AI Logic Enhancement
#### [MODIFY] [ai_utils.py](file:///ai_utils.py)
*   **Context Integration**:
    *   Update `analyze_log` to accept `context_docs` (retrieved SOP snippets).
    *   **Prompt Update**: "You are auditing against *specific* regulations. Here are the relevant SOP sections: {context_docs}..."

### 3. User Interface Upgrades
#### [MODIFY] [app.py](file:///app.py)
*   **Sidebar**: Add "📚 Knowledge Base (Phase 2)" section.
    *   File Uploader for SOPs/Regulations (PDF).
    *   "Process Knowledge Base" button.
*   **Visualization Dashboard**:
    *   **Audit Trends**: Line chart of "Events Over Time".
    *   **User Activity**: Bar chart of "Actions per User".
    *   **Anomaly Heatmap**: Visualizing where potential issues cluster.

### 4. Dependencies
#### [MODIFY] [requirements.txt](file:///requirements.txt)
*   Add: `langchain`, `langchain-community`, `langchain-google-genai`, `chromadb`, `plotly`.

## Verification Plan

## AI Prompt Optimization
- [ ] Apply "Audit Regulation Compliance" guidelines from text file
- [ ] Refine System Prompt for clearer Korean output and logic

### Automated Tests
*   **RAG Test**: Create a dummy SOP (e.g., "Passwords must be 12 chars"). Feed a log with an 8-char password. Verify AI cites the dummy SOP.

### Manual Verification
1.  **Upload SOP**: Upload a PDF of "21 CFR Part 11" or a mock company policy.
2.  **Upload Log**: Upload a log file.
3.  **Analyze**: Check if the AI response quotes specific sections from the uploaded SOP.
4.  **Confirm Phase 2 Completion**: Ensure the "Structural Learning" milestone is met.
