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
        Phase 5 Expert Optimization Implementation:
        - Strategy 1: Sliding Window with Overlap (Context Continuity).
        - Strategy 2: Safe JSON Parsing & Deduplication (Structure).
        - Strategy 3: Deterministic Verification Loop (Anti-Hallucination).
        - Strategy 4: Enhanced Prompting (CoT & Bilingual).
        """
        if not os.getenv("GEMINI_API_KEY"):
            return "Error: API Key is missing."

        # --- Phase 2: Modular Few-Shot Examples ---
        try:
            from prompts.audit_examples import get_examples
            examples = get_examples(equipment_type="COMMON") 
        except ImportError:
            examples = []
        
        example_text = "\\n".join([f"- Example: {ex['scenario']}\\n  Log: {ex['log_snippet']}\\n  Analysis: {ex['analysis']}" for ex in examples])

        # --- Strategy 1: Sliding Window w/ Overlap ---
        chunk_size = 20000
        overlap = 2000
        chunks = []
        if len(log_data) <= chunk_size:
            chunks.append(log_data)
        else:
            # Create overlapping chunks
            for i in range(0, len(log_data), chunk_size - overlap):
                chunks.append(log_data[i : i + chunk_size])

        # --- Execution Mode Split ---
        if user_query:
            return self._handle_chat_mode(chunks, user_query, example_text)
        else:
            return self._handle_audit_mode(chunks, example_text, log_data) # Pass full log for verification

    def _handle_chat_mode(self, chunks, user_query, example_text):
        """Phase 1 & 4: Logic for Interactive Chat (Text/Markdown)"""
        full_response = []
        # For chat, we might restrict to top chunks or summarize, but for now process all (or first few?)
        # To avoid massive costs/latency on huge logs for simple chat, maybe just look at first chunk or Retrieval?
        # For this prototype, we'll process the first 3 chunks max to be safe/responsive.
        for i, chunk in enumerate(chunks[:3]):
            prompt = f"""
            ### ROLE & CONTEXT
            You are a Lead Data Integrity Auditor.
            Review the log chunk below.
            
            ### FEW-SHOT EXAMPLES
            {example_text}

            ### USER QUESTION
            {user_query}

            ### INSTRUCTION
            Answer the user's question based on the log chunk provided.
            
            **STEP 1: ENGLISH RESPONSE**
            - Answer in clear, professional English.
            - **Use this EXACT format for each finding:**
            
              **[Finding #]**
              - **Severity:** ...
              - **Category:** ...
              - **Evidence:** ...
              - **Impact:** ...
              
              ---
              
            - **CRITICAL:** Keep internal lines TIGHT. Use separate findings only for distinct points.

            **STEP 2: KOREAN TRANSLATION (Verification)**
            - Provide a Korean Translation below a separator.
            - Follow the SAME formatting rules.
            
            **OUTPUT FORMAT:**
            [English Findings]
            
            ==================================================
            
            [Korean Translation]
            
            LOG CHUNK {i+1}:
            {chunk}
            """
            try:
                response = self._generate_content_with_retry(contents=[prompt])
                full_response.append(response.text)
            except Exception as e:
                full_response.append(f"Error in chunk {i}: {e}")
        
        return "\n\n".join(full_response)

    def _handle_audit_mode(self, chunks, example_text, full_log_data):
        """Phase 5: Logic for Full Audit (Strict JSON + Verification)"""
        import json
        import re

        all_findings = []
        executive_summaries = []
        recommendations = set()
        compliance_votes = []

        system_instruction = f"""
        ### ROLE
        You are a **Lead Data Integrity (DI) Auditor**.
        Your job is to audit GMP Computerized System logs for **21 CFR Part 11** and **ALCOA+**.
        **Report only with EXPLICIT EVIDENCE.**

        ### FEW-SHOT EXAMPLES
        {example_text}

        ### GROUNDING RULES
        - **Citation**: Quote the exact [Timestamp] and log content.
        - **No Hallucination**: If not found, do not invent.

        ### OUTPUT FORMAT (JSON)
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
                    "evidence": "Log snippet (EXACT QUOTE)",
                    "regulation": "21 CFR Part 11... or ALCOA+..."
                }}
            ],
            "recommendations": ["Action item 1", "Action item 2"]
        }}
        """

        for i, chunk in enumerate(chunks):
            prompt = f"""
            {system_instruction}

            ### INSTRUCTION
            Analyze this log chunk and produce a **JSON** report.
            
            LOG CHUNK {i+1}:
            {chunk}
            
            Output JSON:
            """
            try:
                response = self._generate_content_with_retry(
                    contents=[prompt], 
                    config=types.GenerateContentConfig(temperature=0.0, response_mime_type="application/json")
                )
                
                # --- Strategy 2: Safe JSON Parsing ---
                # Clean potential markdown wrappers
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                chunk_result = json.loads(clean_json)

                # Collect high-level info
                compliance_votes.append(chunk_result.get("compliance_status", "UNKNOWN"))
                executive_summaries.append(chunk_result.get("executive_summary", ""))
                recommendations.update(chunk_result.get("recommendations", []))

                # --- Strategy 3: Deterministic Verification Loop ---
                # Verify if 'evidence' actually exists in the Full Log (or Chunk)
                # We check Full Log to be safe against boundary cuts, though chunk is safer for speed.
                # Since we have full_log_data, let's check there.
                
                raw_findings = chunk_result.get("findings", [])
                for finding in raw_findings:
                    evidence_snippet = finding.get("evidence", "").strip()
                    if not evidence_snippet:
                        continue # Skip empty evidence
                    
                    # Verification: Check if evidence substring is in the original log text
                    if evidence_snippet in full_log_data:
                        all_findings.append(finding)
                    else:
                        logger.warning(f"Strategy 3: Finding discarded due to lack of evidence verification: {finding}")
                        # Optional: Add with a flag? For now, implementing "Conservative Approach" -> Discard.

            except Exception as e:
                logger.error(f"Audit processing failed for chunk {i}: {e}")
        
        # --- Strategy 2: Deduplication ---
        # Deduplicate based on distinct timestamps and evidence
        unique_findings = []
        seen = set()
        for f in all_findings:
            # Create a unique signature
            sig = f"{f.get('timestamp')}|{f.get('evidence')}|{f.get('category')}"
            if sig not in seen:
                unique_findings.append(f)
                seen.add(sig)

        # Determine Final Status (Worst Case)
        final_status = "COMPLIANT"
        if "NON_COMPLIANT" in compliance_votes:
            final_status = "NON_COMPLIANT"
        elif "WARNING" in compliance_votes:
            final_status = "WARNING"
            
        final_summary = " | ".join(filter(None, executive_summaries))

        final_report = {
            "compliance_status": final_status,
            "executive_summary": final_summary if final_summary else "Audit completed.",
            "findings": unique_findings,
            "recommendations": list(recommendations)
        }
        
        return json.dumps(final_report, ensure_ascii=False)
