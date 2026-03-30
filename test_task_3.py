import pytest, os, pandas as pd
from unittest.mock import patch, MagicMock
from task_3 import load_text_files, determine_controls, run_kubescape, generate_csv

NO_DIFF_NAMES = "NO DIFFERENCES IN REGARDS TO ELEMENT NAMES\n"
NO_DIFF_REQS  = "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS\n"
DIFF_NAMES    = "Password Policy\nAudit Logs\n"
DIFF_REQS     = "Password Policy,Min 12 chars\nAudit Logs,Retain 90 days\n"

SAMPLE_DF = pd.DataFrame([{
    "FilePath": "test/pod.yaml",
    "Severity": "High",
    "Control name": "C-0220",
    "Failed resources": 2,
    "All Resources": 5,
    "Compliance score": 0.6
}])

# ── Test 1: load_text_files ─────────────────────────────────────────────────
def test_load_text_files():
    with pytest.raises(FileNotFoundError):
        load_text_files("nonexistent.txt", "alsononexistent.txt")

# ── Test 2: determine_controls ──────────────────────────────────────────────
def test_determine_controls(tmp_path):
    with patch("task_3.OUTPUT_DIR", str(tmp_path)):
        result = determine_controls(DIFF_NAMES, DIFF_REQS)

    content = open(result).read()
    assert "NO DIFFERENCES FOUND" not in content
    assert any(c in content for c in ["C-0220", "C-0221", "C-0007", "C-0067"])

# ── Test 3: run_kubescape ───────────────────────────────────────────────────
def test_run_kubescape(tmp_path):
    controls_file = tmp_path / "controls.txt"
    controls_file.write_text("NO DIFFERENCES FOUND\n")

    mock_json = {
        "results": [{
            "resourceID": "test/pod.yaml",
            "controls": [{
                "name": "C-0220",
                "severity": {"severity": "High"},
                "summary": {"failedResources": 1, "allResources": 3, "complianceScore": 0.67}
            }]
        }]
    }

    with patch("task_3.OUTPUT_DIR", str(tmp_path)), \
         patch("subprocess.run"), \
         patch("builtins.open", create=True), \
         patch("json.load", return_value=mock_json):
        df = run_kubescape(str(controls_file), "project-yamls.zip")

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["FilePath", "Severity", "Control name",
                                 "Failed resources", "All Resources", "Compliance score"]

# ── Test 4: generate_csv ────────────────────────────────────────────────────
def test_generate_csv(tmp_path):
    with patch("task_3.OUTPUT_DIR", str(tmp_path)):
        generate_csv(SAMPLE_DF)

    csv_file = tmp_path / "kubescape-results.csv"
    assert csv_file.exists()
    content = csv_file.read_text()
    assert "FilePath" in content
    assert "Severity" in content
    assert "Compliance score" in content


    