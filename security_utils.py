from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import pandas as pd
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityEngine, cls).__new__(cls)
            cls._instance.analyzer = AnalyzerEngine()
            cls._instance.anonymizer = AnonymizerEngine()
            # Session-specific salt for deterministic hashing
            import secrets
            cls._instance.salt = secrets.token_hex(16)
            logger.info("SecurityEngine initialized with Presidio & Session Salt")
        return cls._instance

    def _generate_pseudonym(self, entity_type: str, value: str) -> str:
        """
        Generates a consistent, short pseudonym using HMAC-SHA256.
        Format: Type_HashPrefix (e.g., PERSON_a1b2c3)
        """
        import hashlib
        import hmac
        
        # Use session salt + value to create hash
        hash_obj = hmac.new(self.salt.encode(), value.encode(), hashlib.sha256)
        short_hash = hash_obj.hexdigest()[:6] # First 6 chars are enough for collision resistance in small contexts
        
        # Custom prefixes for readability
        prefix_map = {
            "PERSON": "User",
            "IP_ADDRESS": "IP",
            "EMAIL_ADDRESS": "Email",
            "PHONE_NUMBER": "Phone"
        }
        prefix = prefix_map.get(entity_type, entity_type)
        
        return f"<{prefix}_{short_hash}>"

    def anonymize_text(self, text: str) -> str:
        """
        Analyzes and pseudonymizes PII in the given text using Presidio + Hashing.
        Conserves Referential Integrity (Same input -> Same output).
        """
        if not isinstance(text, str) or not text:
            return text

        try:
            # Analyze
            results = self.analyzer.analyze(text=text, entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "IP_ADDRESS"], language='en')
            
            # Sort results by start index in descending order to replace from end
            # This prevents index shifting issues
            results.sort(key=lambda x: x.start, reverse=True)
            
            anonymized_text = text
            for res in results:
                original_value = text[res.start:res.end]
                pseudonym = self._generate_pseudonym(res.entity_type, original_value)
                
                # Replace in text
                anonymized_text = anonymized_text[:res.start] + pseudonym + anonymized_text[res.end:]
            
            return anonymized_text
        except Exception as e:
            logger.error(f"Error anonymizing text: {e}")
            return text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Anonymizes string columns in a Pandas DataFrame.
        """
        df_masked = df.copy()
        
        # Select string columns (object type)
        obj_cols = df_masked.select_dtypes(include=['object']).columns
        
        for col in obj_cols:
            logger.info(f"Anonymizing column: {col}")
            # Unique values optimization: Anonymize unique values map, then replace
            # This is much faster than applying to every row if there are duplicates
            unique_vals = df_masked[col].dropna().unique()
            val_map = {val: self.anonymize_text(str(val)) for val in unique_vals}
            df_masked[col] = df_masked[col].map(val_map)
            
        return df_masked
