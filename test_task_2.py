import pytest, os
from unittest.mock import patch
from task_2 import load_yaml_files, compare_element_names, compare_element_requirements

SAMPLE_YAML1 = {
    "zero-shot": {
        "element1": {"name": "Password Policy", "requirements": ["Min 12 chars", "Must have symbols"]},
        "element2": {"name": "Network Encryption", "requirements": ["TLS 1.2 required"]}
    }
}

SAMPLE_YAML2 = {
    "zero-shot": {
        "element1": {"name": "Password Policy", "requirements": ["Min 12 chars"]},
        "element2": {"name": "Audit Logs", "requirements": ["Logs must be retained 90 days"]}
    }
}

# ── Test 1: load_yaml_files ─────────────────────────────────────────────────
def test_load_yaml_files():
    with pytest.raises(FileNotFoundError):
        load_yaml_files("nonexistent.yaml", "alsononexistent.yaml")

# ── Test 2: compare_element_names ───────────────────────────────────────────
def test_compare_element_names(tmp_path):
    with patch("task_2.OUTPUT_DIR", str(tmp_path)):
        compare_element_names(SAMPLE_YAML1, SAMPLE_YAML2)

    output = (tmp_path / "element_name_differences.txt").read_text()
    assert "Network Encryption" in output or "Audit Logs" in output
    assert "NO DIFFERENCES" not in output

# ── Test 3: compare_element_requirements ────────────────────────────────────
def test_compare_element_requirements(tmp_path):
    with patch("task_2.OUTPUT_DIR", str(tmp_path)):
        compare_element_requirements(SAMPLE_YAML1, SAMPLE_YAML2)

    output = (tmp_path / "element_requirement_differences.txt").read_text()
    assert "," in output  # NAME,REQU format
    assert "NO DIFFERENCES" not in output