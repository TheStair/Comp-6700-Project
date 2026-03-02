import pytest, os, yaml
from unittest.mock import patch, MagicMock
from task_1 import (
    load_documents,
    construct_zero_shot,
    construct_few_shot,
    construct_cot,
    extract_kdes,
    collect_output
)

# ── Test 1: load_documents ──────────────────────────────────────────────────
def test_load_documents():
    with pytest.raises(FileNotFoundError):
        load_documents("nonexistent.pdf", "alsononexistent.pdf")

# ── Test 2: construct_zero_shot ─────────────────────────────────────────────
def test_construct_zero_shot():
    result = construct_zero_shot("test document text")
    assert isinstance(result, str)
    assert "test document text" in result
    assert "YAML" in result

# ── Test 3: construct_few_shot ──────────────────────────────────────────────
def test_construct_few_shot():
    result = construct_few_shot("test document text")
    assert isinstance(result, str)
    assert "test document text" in result
    assert "example" in result.lower()

# ── Test 4: construct_cot ───────────────────────────────────────────────────
def test_construct_cot():
    result = construct_cot("test document text")
    assert isinstance(result, str)
    assert "test document text" in result
    assert "YAML OUTPUT:" in result

# ── Test 5: extract_kdes ────────────────────────────────────────────────────
def test_extract_kdes(tmp_path):
    mock_output = [[{
        "generated_text": [
            {"role": "user", "content": "prompt"},
            {"role": "assistant", "content": "element1:\n  name: Test\n  requirements:\n    - req1\n"}
        ]
    }]]

    with patch("pipeline.pipe", return_value=mock_output):
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF-1.4 test")  # minimal fake pdf
        result = extract_kdes("some document text", str(dummy_pdf))

    assert isinstance(result, dict)
    assert "zero-shot" in result

# ── Test 6: collect_output ──────────────────────────────────────────────────
def test_collect_output(tmp_path):
    with patch("pipeline.OUTPUT_DIR", str(tmp_path)):
        collect_output(
            llm_name="google/gemma-3-1b-it",
            prompt="test prompt",
            prompt_type="zero-shot",
            llm_output="test output",
            output_file="test_output.txt"
        )
    
    output_file = tmp_path / "test_output.txt"
    assert output_file.exists()
    content = output_file.read_text()
    assert "*LLM Name*" in content
    assert "google/gemma-3-1b-it" in content
    assert "*Prompt Type*" in content
    assert "zero-shot" in content