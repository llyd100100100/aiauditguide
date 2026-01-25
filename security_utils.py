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
            logger.info("SecurityEngine initialized with Presidio Analyzer & Anonymizer")
        return cls._instance

    def anonymize_text(self, text: str) -> str:
        """
        Analyzes and anonymizes PII in the given text using Presidio.
        """
        if not isinstance(text, str) or not text:
            return text

        try:
            # Analyze
            results = self.analyzer.analyze(text=text, entities=["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "IP_ADDRESS"], language='en')
            
            # Anonymize with replacement tags
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators={
                    "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
                    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
                    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
                    "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP_ADDRESS>"}),
                }
            )
            return anonymized_result.text
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
