from google import genai
from google.genai import types
import os
import logging
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions

load_dotenv()
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self, model_id="gemini-flash-latest"):
        self.model_id = model_id
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=api_key)

    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        stop=stop_after_attempt(7),
        wait=wait_exponential(multiplier=2, min=5, max=60)
    )
    def _generate_content_with_retry(self, contents, config=None):
        if config is None:
            config = types.GenerateContentConfig(
                temperature=0.1, 
            )
        return self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config
        )

    def analyze_log(self, log_data: str, user_query: str = "") -> str:
        """
        Phase 0, 1, 2, 3, 4 Implementation:
        - Phase 0: Sliding Window (Chunking) to handle large logs.
        - Phase 1: Persona & CoT (Chain of Thought).
        - Phase 2: Modular Few-Shot Examples (Examples Lib).
        - Phase 3: Grounding (Citation).
        - Phase 4: Structured Output (JSON).
        """
        if not os.getenv("GEMINI_API_KEY"):
            return "Error: API Key is missing."

        # --- Phase 2: Modular Few-Shot Examples (Refactored) ---
        # Load examples from the dedicated library
        try:
            from prompts.audit_examples import get_examples
            # Default to COMMON + HPLC for now (or make it selectable in future)
            examples = get_examples(equipment_type="COMMON") 
        except ImportError:
            # Fallback if file missing
            examples = []

        example_text = "\\n".join([f"- Example: {ex['scenario']}\\n  Log: {ex['log_snippet']}\\n  Analysis: {ex['analysis']}" for ex in examples])

        # --- Phase 1: Persona & CoT System Prompt ---
        system_instruction = f"""
        ### ROLE
        You are a **Lead Data Integrity (DI) Auditor** with 20+ years of experience in QA.
        Your job is to audit GMP Computerized System logs for **21 CFR Part 11** and **ALCOA+** compliance.
        You are **skeptical, evidence-based, and conservative**. Do not guess.

        ### PROCESS (Chain-of-Thought)
        1. **Identify**: Who is acting? (Shared accounts like 'Admin'? Unauthorized roles?)
        2. **Timeline**: Are there timestamps out of order? Long gaps? Back-dating?
        3. **Action**: Look for DELETE, MODIFY, ABORT, RENAME. Is there a 'Reason' field?
        4. **Pattern**: Detect 'Testing into Compliance' (Repeated testing until pass).

        ### FEW-SHOT EXAMPLES (Reference)
        {example_text}

        ### GROUNDING RULES (Phase 3)
        - **Citation**: Every finding MUST quote the exact [Line Number] and [Timestamp] from the log.
        - **No Hallucination**: If the log says nothing, state "No evidence found". Do not invent events.

        ### OUTPUT FORMAT (Phase 4: JSON)
        Produce a valid **JSON** object with the following schema:
        {{
            "compliance_status": "COMPLIANT" | "WARNING" | "NON_COMPLIANT",
            "executive_summary": "Brief summary in English then Korean...",
            "findings": [
                {{
                    "timestamp": "YYYY-MM-DD HH:MM:SS",
                    "user_id": "UserID",
                    "severity": "CRITICAL" | "MAJOR" | "MINOR",
                    "category": "Data Deletion" | "Testing into Compliance" | "Unauthoried Access" | "Other",
                    "description": "Description in English then Korean...",
                    "evidence": "Log snippet...",
                    "regulation": "21 CFR Part 11... or ALCOA+..."
                }}
            ],
            "recommendations": ["Action item 1 (English/Korean)", "Action item 2"]
        }}
        **IMPORTANT: Output ONLY JSON. All descriptions must be in English first, followed by Korean translation.**
        """

        # --- Phase 0: Sliding Window Strategy ---
        # Simple chunking for now (can be enhanced to true sliding window with overlap later)
        chunk_size = 20000 # Approx characters
        chunks = [log_data[i:i+chunk_size] for i in range(0, len(log_data), chunk_size)]
        
        full_report = []
        
        for i, chunk in enumerate(chunks):
            if user_query:
                # --- Chat Mode (Markdown) ---
                # Relaxed constraint for chat, specifically asking for spacing
                prompt = f"""
                {system_instruction}

                ### USER QUESTION
                {user_query}

                ### INSTRUCTION
                Answer the user's question based on the log chunk provided.
                
                **STEP 1: ENGLISH RESPONSE**
                - Answer in clear, professional English.
                - Use bullet points.
                - Keep related lines TIGHT (single spacing).
                - Use DOUBLE NEWLINE only between major points/findings.

                **STEP 2: KOREAN TRANSLATION (Verification)**
                - You MUST provide a **Korean Translation** of your answer below a separator.
                - Translate accurately and naturally for a Korean auditor.
                
                **OUTPUT FORMAT:**
                [English Answer]
                
                --- (Separator)
                
                [Korean Translation]
                
                LOG CHUNK {i+1}:
                {chunk}
                """
                config = types.GenerateContentConfig(temperature=0.3) # Slightly creative for chat
                
            else:
                # --- Audit Mode (JSON) ---
                # Strict JSON constraint
                prompt = f"""
                {system_instruction}

                ### INSTRUCTION
                Analyze this log chunk and produce a **JSON** report.
                
                LOG CHUNK {i+1}:
                {chunk}
                
                Output JSON:
                """
                config = types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json"
                )

            try:
                # Using the internal method with retry logic settings
                response = self._generate_content_with_retry(contents=[prompt], config=config)
                full_report.append(response.text)
            except Exception as e:
                logger.error(f"AI Analysis failed for chunk {i}: {e}")
                full_report.append(f'{{"error": "Analysis failed for chunk {i}: {str(e)}"}}')

        # Aggregate results (Simple concatenation for now, ideal would be merging JSONs)
        # Since the user wants a single report, we might need to merge them.
        # For this step, we will return the first chunk's result or a list if multiple.
        if len(full_report) == 1:
            return full_report[0]
        else:
             # Naive aggregation for multiple chunks
            return f"[{','.join(full_report)}]"
