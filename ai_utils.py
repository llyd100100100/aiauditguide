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
    def __init__(self):
        # Using 'gemini-flash-latest' alias which appeared in the user's available model list
        self.model_id = "gemini-flash-latest" 
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables.")
        
        self.client = genai.Client(api_key=api_key)

    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        stop=stop_after_attempt(7),
        wait=wait_exponential(multiplier=2, min=5, max=60)
    )
    def _generate_content_with_retry(self, prompt, context):
        return self.client.models.generate_content(
            model=self.model_id,
            contents=[prompt, context],
            config=types.GenerateContentConfig(
                temperature=0.1, 
            )
        )

    def analyze_log(self, log_data: str, user_query: str = "") -> str:
        """
        Sends audit trail logs to Gemini for GMP Data Integrity compliance analysis.
        Focuses on ALCOA+ principles and 21 CFR Part 11 requirements.
        """
        if not os.getenv("GEMINI_API_KEY"):
            return "Error: API Key is missing."

        # GMP/DI 특화 프롬프트
        system_instruction = """
        ### ROLE
        You are a **Lead Data Integrity (DI) Auditor** in a pharmaceutical company. 
        Your responsibility is to review the Audit Trail logs of a GMP Computerized System to ensure compliance with **21 CFR Part 11**, **EudraLex Annex 11**, and **ALCOA+ principles**.

        ### CONTEXT & RULES
        - The input data consists of anonymized audit trail logs (<USER>, <TIMESTAMP>, <ACTION>, <VALUE>).
        - **Objective:** Detect potential Data Integrity (DI) violations, data manipulation, or bad practices.
        - **Zero Tolerance:** Treat any deletion of raw data or modification of critical parameters without a clear reason as a CRITICAL violation.

        ### AUDIT FRAMEWORK (ALCOA+ Focus)
        Analyze the logs specifically for the following scenarios:

        1. **Attributability (Who):** - Detect usage of shared/generic accounts (e.g., "Admin", "User1"). 
           - Detect actions performed by unauthorized roles (e.g., an Operator deleting a method).
        2. **Legibility & Originality:** - Flag any "DELETE", "DROP", or "REMOVE" actions on data files or test results.
           - Identify changes to "Audit Trail Configuration" (e.g., turning off the audit trail).
        3. **Contemporaneous (When):** - Detect non-chronological timestamps (potential system clock manipulation/backdating).
           - Identify suspicious activity during non-business hours without justification.
        4. **Testing into Compliance (Fraud):**
           - Look for repeated "Aborted" runs followed by a "Passed" run.
           - Look for multiple modifications of "Integration Parameters" or "Processing Methods" immediately prior to a result generation.

        ### OUTPUT FORMAT (Strict Markdown)
        Produce a formal **Audit Review Report**:

        #### 1. Compliance Summary
        - Assessment: [COMPLIANT / MINOR OBSERVATION / MAJOR OBSERVATION / CRITICAL WARNING]
        - Summary of the audit trail review.

        #### 2. DI Observations (Findings)
        (List each finding clearly)
        - **Severity:** [Critical / Major / Minor]
        - **Category:** (e.g., Unauthorized Deletion, Testing into Compliance, Invalid User Access)
        - **Log Evidence:** (Quote the specific log entry)
        - **Regulatory Impact:** (Explain which principle of ALCOA+ or 21 CFR Part 11 is violated. E.g., *"Violates 'Original' principle by destroying raw data."*)

        #### 3. Auditor Recommendations
        - Immediate actions required (e.g., "Initiate Deviation Report", "Lock user account <USER_A>").
        """
             
        if user_query:
            prompt = f"{system_instruction}\n\nUSER QUESTION: {user_query}\n\nPlease answer the user's question based on the provided logs."
        else:
            prompt = f"{system_instruction}\n\nPerform a comprehensive security audit summary."

        try:
            # Using the internal method with retry logic
            response = self._generate_content_with_retry(prompt, log_data)
            return response.text
        except Exception as e:
            logger.error(f"AI Analysis failed: {e}")
            return f"Error during AI analysis (after retries): {str(e)}"
