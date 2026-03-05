import subprocess
import sys

COMBINATIONS = [
    ("cis-r1.pdf", "cis-r1.pdf"),
    ("cis-r1.pdf", "cis-r2.pdf"),
    ("cis-r1.pdf", "cis-r3.pdf"),
    ("cis-r1.pdf", "cis-r4.pdf"),
    ("cis-r2.pdf", "cis-r2.pdf"),
    ("cis-r2.pdf", "cis-r3.pdf"),
    ("cis-r2.pdf", "cis-r4.pdf"),
    ("cis-r3.pdf", "cis-r3.pdf"),
    ("cis-r3.pdf", "cis-r4.pdf"),
]

INPUT_DIR = "input_files/"

for doc1, doc2 in COMBINATIONS:
    path1 = INPUT_DIR + doc1
    path2 = INPUT_DIR + doc2
    print(f"\nRunning: {doc1} + {doc2}")
    result = subprocess.run(
        [sys.executable, "pipeline.py", path1, path2],
    )
    if result.returncode != 0:
        print(f"Failed on {doc1} + {doc2}")