# Comp-6700-Project
Final Project for Secure Software Process - Comp 6700 - at Auburn

## Team Members
Marshall Nelson - man0054  
Blake Werk - jbw0082

## LLM
 
This project uses **google/gemma-3-1b-it** via HuggingFace Transformers for all KDE extraction tasks (Task-1).

Claude Sonnet 4.3 was used in the development of this project
 
## Repository Structure
 
```
├── .github/workflows/ci.yml    # GitHub Actions workflow
├── input_files/                 # CIS benchmark PDFs
│   ├── cis-r1.pdf
│   ├── cis-r2.pdf
│   ├── cis-r3.pdf
│   └── cis-r4.pdf
├── sample_output/               # Pre-generated output for reference
├── task_1.py                    # Extractor — PDF loading, prompts, KDE extraction
├── task_2.py                    # Comparator — YAML diffing for names and requirements
├── task_3.py                    # Executor — Kubescape control mapping and scanning
├── pipeline.py                  # End-to-end pipeline (single input pair)
├── run_all.py                   # Runs pipeline over all 9 input combinations
├── test_task_1.py               # Unit tests for Task-1 (6 tests)
├── test_task_2.py               # Unit tests for Task-2 (3 tests)
├── test_task_3.py               # Unit tests for Task-3 (4 tests)
├── PROMPT.md                    # All prompts: zero-shot, few-shot, chain-of-thought
├── requirements.txt             # Python dependencies with versions
├── project-yamls.zip            # Kubernetes YAML files for Kubescape scanning
```
 
## Setup and Installation
 
### Prerequisites
 
- Python 3.9+
- Kubescape (installed automatically in CI, or manually via the command below)
- A HuggingFace account with access to `google/gemma-3-1b-it`
 
### Virtual Environment Setup
 
```bash
python3 -m venv comp6700-venv
source comp6700-venv/bin/activate
pip install -r requirements.txt
```
 
### Kubescape Installation
 
```bash
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
```
 
### HuggingFace Authentication
 
The Gemma model requires authentication. Log in before running:
 
```bash
pip install huggingface_hub
huggingface-cli login
```
 
## Running the Project
 
### Option 1: Python (Single Input Pair)
 
```bash
python3 pipeline.py input_files/cis-r1.pdf input_files/cis-r2.pdf
```
 
### Option 2: Python (All 9 Input Combinations)
 
```bash
python3 run_all.py
```
 
This runs the pipeline for all required input pairs:
 
| Input | Document 1 | Document 2 |
|-------|-----------|-----------|
| 1 | cis-r1.pdf | cis-r1.pdf |
| 2 | cis-r1.pdf | cis-r2.pdf |
| 3 | cis-r1.pdf | cis-r3.pdf |
| 4 | cis-r1.pdf | cis-r4.pdf |
| 5 | cis-r2.pdf | cis-r2.pdf |
| 6 | cis-r2.pdf | cis-r3.pdf |
| 7 | cis-r2.pdf | cis-r4.pdf |
| 8 | cis-r3.pdf | cis-r3.pdf |
| 9 | cis-r3.pdf | cis-r4.pdf |
 
### Option 3: PyInstaller Binary

Our PyInstaller Binaries were too large for GitHub when including everything.
 
Pre-built binaries are available in [this box folder](https://auburn.box.com/s/f9eiqi0wrfb2e7413fcx667jsjgk7ds9)
 
**Linux:**
```bash
./dist/pipeline input_files/cis-r1.pdf input_files/cis-r2.pdf
```
 
**Windows:**
```powershell
.\dist\pipeline.exe input_files\cis-r1.pdf input_files\cis-r2.pdf
```
 
Note: The binary is self-contained and does not require a virtual environment. However, Kubescape must still be installed on the system for Task-3. The Gemma model will be downloaded from HuggingFace on first run if not already cached.
 
## Output
 
All output files are written to the `output/` directory:
 
| File | Description | Task |
|------|------------|------|
| `*-kdes.yaml` | Extracted KDEs per document (one per PDF) | Task-1 |
| `llm_outputs.txt` | Formatted LLM output log | Task-1 |
| `element_name_differences.txt` | Differences in KDE names | Task-2 |
| `element_requirement_differences.txt` | Differences in KDE requirements (NAME,REQU tuples) | Task-2 |
| `controls.txt` | Mapped Kubescape controls or "NO DIFFERENCES FOUND" | Task-3 |
| `kubescape-results.csv` | Scan results with FilePath, Severity, Control name, Failed resources, All Resources, Compliance score | Task-3 |
 
Pre-generated sample output is available in `sample_output/` for reference.
 
## Running Tests
 
```bash
pytest test_task_1.py test_task_2.py test_task_3.py -v
```
 
Tests are also run automatically via GitHub Actions on every push and pull request.
 
## Building the Binaries
 
If you need to rebuild the binaries from source:
 
```bash
pip install pyinstaller
pyinstaller --onefile pipeline.py --name pipeline
```
 
The binary will be placed in `dist/`. PyInstaller produces a platform-native binary, so build on Linux for ELF and on Windows for PE.
