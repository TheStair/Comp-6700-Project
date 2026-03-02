import yaml, os, sys

OUTPUT_DIR = "output"

def load_yaml_files(path1: str, path2: str) -> tuple[dict, dict]:
    """Takes two YAML filepaths, validates them, returns parsed dicts."""
    for path in (path1, path2):
        if not isinstance(path, str):
            raise TypeError(f"Expected string filepath, got {type(path)}")
        if not path:
            raise ValueError("Filepath cannot be empty")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {path}")
        if not path.lower().endswith(".yaml"):
            raise ValueError(f"File must be a YAML: {path}")
        if os.path.getsize(path) == 0:
            raise ValueError(f"File is empty: {path}")

    with open(path1) as f:
        yaml1 = yaml.safe_load(f)
    with open(path2) as f:
        yaml2 = yaml.safe_load(f)

    return yaml1, yaml2


def compare_element_names(yaml1: dict, yaml2: dict, output_file: str = "element_name_differences.txt") -> None:
    """Compares KDE names across two YAML dicts, writes differences to TEXT file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def get_names(yaml_dict: dict) -> set[str]:
        names = set()
        for prompt_type, elements in yaml_dict.items():
            if isinstance(elements, dict):
                for key, val in elements.items():
                    if isinstance(val, dict) and "name" in val:
                        names.add(val["name"])
        return names

    names1 = get_names(yaml1)
    names2 = get_names(yaml2)
    differences = names1.symmetric_difference(names2)

    with open(os.path.join(OUTPUT_DIR, output_file), "w") as f:
        if not differences:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES\n")
        else:
            for name in sorted(differences):
                f.write(f"{name}\n")


def compare_element_requirements(yaml1: dict, yaml2: dict, output_file: str = "element_requirement_differences.txt") -> None:
    """Compares KDE requirements across two YAML dicts, writes differences as NAME,REQU tuples."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    def get_name_req_pairs(yaml_dict: dict) -> set[tuple[str, str]]:
        pairs = set()
        for prompt_type, elements in yaml_dict.items():
            if isinstance(elements, dict):
                for key, val in elements.items():
                    if isinstance(val, dict) and "name" in val:
                        name = val["name"]
                        for req in val.get("requirements", []):
                            pairs.add((name, str(req)))
        return pairs

    pairs1 = get_name_req_pairs(yaml1)
    pairs2 = get_name_req_pairs(yaml2)
    differences = pairs1.symmetric_difference(pairs2)

    with open(os.path.join(OUTPUT_DIR, output_file), "w") as f:
        if not differences:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS\n")
        else:
            for name, req in sorted(differences):
                f.write(f"{name},{req}\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python task_2.py <yaml1> <yaml2>")
        sys.exit(1)

    path1 = sys.argv[1]
    path2 = sys.argv[2]

    yaml1, yaml2 = load_yaml_files(path1, path2)
    compare_element_names(yaml1, yaml2)
    compare_element_requirements(yaml1, yaml2)