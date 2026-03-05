from task_1 import load_documents, construct_zero_shot, construct_few_shot, construct_cot, extract_kdes, collect_output
from task_2 import load_yaml_files, compare_element_names, compare_element_requirements
from task_3 import load_text_files, determine_controls, run_kubescape, generate_csv
import sys, os

OUTPUT_DIR = "output"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./pipeline <path1> <path2>")
        sys.exit(1)

    path1 = sys.argv[1]
    path2 = sys.argv[2]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    open(os.path.join(OUTPUT_DIR, "llm_outputs.txt"), "w").close()

    # Task 1
    text1, text2 = load_documents(path1, path2)
    kdes1 = extract_kdes(text1, path1, chunk=True)
    kdes2 = extract_kdes(text2, path2, chunk=True)

    # Task 2
    yaml1_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(path1))[0] + "-kdes.yaml")
    yaml2_path = os.path.join(OUTPUT_DIR, os.path.splitext(os.path.basename(path2))[0] + "-kdes.yaml")
    yaml1, yaml2 = load_yaml_files(yaml1_path, yaml2_path)
    compare_element_names(yaml1, yaml2)
    compare_element_requirements(yaml1, yaml2)

    # Task 3
    names_file = os.path.join(OUTPUT_DIR, "element_name_differences.txt")
    reqs_file  = os.path.join(OUTPUT_DIR, "element_requirement_differences.txt")
    names_content, reqs_content = load_text_files(names_file, reqs_file)
    controls_file = determine_controls(names_content, reqs_content)
    df = run_kubescape(controls_file)
    generate_csv(df)