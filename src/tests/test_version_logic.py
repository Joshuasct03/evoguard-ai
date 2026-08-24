import sys
import os
import pytest

# Point to the src folder so pytest can import your custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from version_logic import evaluate_api_safety

@pytest.fixture
def sample_api_data():
    return {
        "api": "torch.lstsq",
        "status": "deprecated",
        "deprecated_in": "1.9.0",
        "removed_in": "2.0.0",
        "replacement": "torch.linalg.lstsq"
    }

def test_safe_version(sample_api_data):
    result = evaluate_api_safety(sample_api_data, "1.8.0")
    assert "SAFE" in result

def test_warning_version(sample_api_data):
    result = evaluate_api_safety(sample_api_data, "1.9.5")
    assert "WARNING" in result

def test_danger_version(sample_api_data):
    result = evaluate_api_safety(sample_api_data, "2.0.1")
    assert "DANGER" in result

def test_missing_evidence():
    result = evaluate_api_safety({}, "1.0.0")
    assert "UNKNOWN" in result