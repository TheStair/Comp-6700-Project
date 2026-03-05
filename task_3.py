import os, sys, json, subprocess, pandas as pd
from pathlib import Path

OUTPUT_DIR = "output"

# Kubescape to CIS control mapping
CONTROL_MAPPING = {
    "Password Policy":        ["C-0220", "C-0221"],
    "Network Encryption":     ["C-0078", "C-0079"],
    "Audit Logs":             ["C-0007", "C-0067"],
    "Network Configuration":  ["C-0035", "C-0074"],
    "User Credentials":       ["C-0015", "C-0220"],
    "Access Control":         ["C-0063", "C-0065"],
    "File Permissions":       ["C-0045", "C-0046"],
    "Service Configuration":  ["C-0016", "C-0021"],
}


def load_text_files(names_file: str, reqs_file: str) -> tuple[str, str]:
    """Takes two TEXT filepaths from Task-2, validates them, returns contents."""
    for path in (names_file, reqs_file):
        if not isinstance(path, str):
            raise TypeError(f"Expected string filepath, got {type(path)}")
        if not path:
            raise ValueError("Filepath cannot be empty")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {path}")
        if not path.lower().endswith(".txt"):
            raise ValueError(f"File must be a .txt file: {path}")
        if os.path.getsize(path) == 0:
            raise ValueError(f"File is empty: {path}")

    with open(names_file) as f:
        names_content = f.read()
    with open(reqs_file) as f:
        reqs_content = f.read()

    return names_content, reqs_content


def determine_controls(names_content: str, reqs_content: str, output_file: str = "controls.txt") -> str:
    """Determines Kubescape controls from differences, writes to TEXT file, returns filepath."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_file)

    no_name_diffs = "NO DIFFERENCES IN REGARDS TO ELEMENT NAMES" in names_content
    no_req_diffs  = "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS" in reqs_content

    if no_name_diffs and no_req_diffs:
        with open(output_path, "w") as f:
            f.write("NO DIFFERENCES FOUND\n")
        return output_path

    # Collect all differing element names
    controls = set()
    for line in (names_content + "\n" + reqs_content).splitlines():
        line = line.strip()
        if not line:
            continue
        # Check name directly
        for kde_name, kde_controls in CONTROL_MAPPING.items():
            if kde_name.lower() in line.lower():
                controls.update(kde_controls)
        # Also check NAME from NAME,REQU tuples
        if "," in line:
            name_part = line.split(",")[0].strip()
            for kde_name, kde_controls in CONTROL_MAPPING.items():
                if kde_name.lower() in name_part.lower():
                    controls.update(kde_controls)

    with open(output_path, "w") as f:
        if controls:
            for control in sorted(controls):
                f.write(f"{control}\n")
        else:
            # Differences exist but no mapping found — run all controls
            f.write("RUN ALL\n")

    return output_path


def run_kubescape(controls_file: str, yamls_zip: str = "project-yamls.zip") -> pd.DataFrame:
    """Runs Kubescape on project-yamls.zip based on controls file, returns results as DataFrame."""
    with open(controls_file) as f:
        content = f.read().strip()

    # Unzip the yamls
    unzip_dir = os.path.join(OUTPUT_DIR, "project-yamls")
    os.makedirs(unzip_dir, exist_ok=True)
    subprocess.run(["unzip", "-o", yamls_zip, "-d", unzip_dir], check=True)

    results_json = os.path.join(OUTPUT_DIR, "kubescape-results.json")

    if "NO DIFFERENCES FOUND" in content or "RUN ALL" in content:
        cmd = ["kubescape", "scan", unzip_dir, "--format", "json", "--output", results_json]
    else:
        controls = [line.strip() for line in content.splitlines() if line.strip()]
        controls_str = ",".join(controls)
        cmd = ["kubescape", "scan", "control", controls_str, unzip_dir,
               "--format", "json", "--output", results_json]

    subprocess.run(cmd, check=True)

    with open(results_json) as f:
        data = json.load(f)

    rows = []
    for result in data.get("results", []):
        resource_id = result.get("resourceID", "")
        for control in result.get("controls", []):
            status = control.get("status", {}).get("status", "")
            rules = control.get("rules", [])
            failed = sum(1 for r in rules if r.get("status") == "failed")
            total = len(rules)
            compliance = round((total - failed) / total, 2) if total > 0 else 0.0

            rows.append({
                "FilePath":         resource_id,
                "Severity":         control.get("severity", ""),
                "Control name":     control.get("name", ""),
                "Failed resources": failed,
                "All Resources":    total,
                "Compliance score": compliance,
            })

    return pd.DataFrame(rows, columns=["FilePath", "Severity", "Control name",
                                        "Failed resources", "All Resources", "Compliance score"])


def generate_csv(df: pd.DataFrame, output_file: str = "kubescape-results.csv") -> None:
    """Writes kubescape results DataFrame to CSV file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUTPUT_DIR, output_file), index=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python task_3.py <names_diff.txt> <reqs_diff.txt>")
        sys.exit(1)

    names_file = sys.argv[1]
    reqs_file  = sys.argv[2]

    names_content, reqs_content = load_text_files(names_file, reqs_file)
    controls_file = determine_controls(names_content, reqs_content)
    df = run_kubescape(controls_file)
    generate_csv(df)