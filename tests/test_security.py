import pytest
import pandas as pd
from security_utils import SecurityEngine

@pytest.fixture(scope="module")
def security_engine():
    return SecurityEngine()

def test_anonymize_text_person(security_engine):
    raw_text = "John Doe tried to login."
    masked_text = security_engine.anonymize_text(raw_text)
    # Check for User_ prefix
    assert "<User_" in masked_text
    assert "John Doe" not in masked_text

def test_anonymize_text_ip(security_engine):
    raw_text = "Connection from 192.168.1.1 refused."
    masked_text = security_engine.anonymize_text(raw_text)
    # Check for IP_ prefix
    assert "<IP_" in masked_text
    assert "192.168.1.1" not in masked_text

def test_determinism(security_engine):
    text1 = "Alice accessed the server."
    text2 = "Alice accessed the server."
    
    masked1 = security_engine.anonymize_text(text1)
    masked2 = security_engine.anonymize_text(text2)
    
    assert masked1 == masked2
    assert "<User_" in masked1

def test_differentiation(security_engine):
    text1 = "Alice logged in."
    text2 = "Bob logged in."
    
    masked1 = security_engine.anonymize_text(text1)
    masked2 = security_engine.anonymize_text(text2)
    
    # Hashes should be different
    # Extract the hash part <User_XXXXXX>
    import re
    hash1 = re.search(r"<User_[a-f0-9]+>", masked1).group()
    hash2 = re.search(r"<User_[a-f0-9]+>", masked2).group()
    
    assert hash1 != hash2

def test_anonymize_dataframe(security_engine):
    data = {
        "User": ["Alice Smith", "Bob Jones"],
        "Action": ["Login", "Logout"],
        "IP": ["10.0.0.1", "10.0.0.2"]
    }
    df = pd.DataFrame(data)
    
    masked_df = security_engine.anonymize_dataframe(df)
    
    # Check User column
    assert "<User_" in masked_df["User"].iloc[0]
    assert "Alice Smith" not in masked_df["User"].iloc[0]
    
    # Check IP column
    assert "<IP_" in masked_df["IP"].iloc[0]
    assert "10.0.0.1" not in masked_df["IP"].iloc[0]
