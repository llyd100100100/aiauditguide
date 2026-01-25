import pytest
import pandas as pd
from security_utils import SecurityEngine

@pytest.fixture(scope="module")
def security_engine():
    return SecurityEngine()

def test_anonymize_text_person(security_engine):
    raw_text = "John Doe tried to login."
    masked_text = security_engine.anonymize_text(raw_text)
    assert "<PERSON>" in masked_text
    assert "John Doe" not in masked_text

def test_anonymize_text_ip(security_engine):
    raw_text = "Connection from 192.168.1.1 refused."
    masked_text = security_engine.anonymize_text(raw_text)
    assert "<IP_ADDRESS>" in masked_text
    assert "192.168.1.1" not in masked_text

def test_anonymize_dataframe(security_engine):
    data = {
        "User": ["Alice Smith", "Bob Jones"],
        "Action": ["Login", "Logout"],
        "IP": ["10.0.0.1", "10.0.0.2"]
    }
    df = pd.DataFrame(data)
    
    masked_df = security_engine.anonymize_dataframe(df)
    
    # Check User column
    assert "<PERSON>" in masked_df["User"].iloc[0]
    assert "Alice Smith" not in masked_df["User"].iloc[0]
    
    # Check IP column
    assert "<IP_ADDRESS>" in masked_df["IP"].iloc[0]
    assert "10.0.0.1" not in masked_df["IP"].iloc[0]

    # Check that Action (non-PII) is preserved (mostly)
    # Note: Presidio might flag common words if they look like names, but "Login" should stand unless context implies otherwise.
    # Actually, "Login" is usually safe.
    assert masked_df["Action"].iloc[0] == "Login"
