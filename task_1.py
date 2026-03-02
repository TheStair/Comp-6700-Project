import torch, os, fitz, yaml, sys
from transformers import pipeline

if torch.cuda.is_available():        # CUDA (NVIDIA)
    device = "cuda"
elif torch.backends.mps.is_available():  # Apple Silicon
    device = "mps"
else:
    device = "cpu"

dtype = torch.bfloat16 if device == "cuda" else torch.float32

pipe = pipeline(
    "text-generation",
    model="google/gemma-3-1b-it",
    device=device,
    dtype=dtype
)

input_dir = "input_files/"

def load_documents(path1: str, path2: str) -> tuple[str, str]:
    """Takes two PDF filepaths, validates them, returns extracted text."""
    
    for path in (path1, path2):
        if not isinstance(path, str):
            raise TypeError(f"Expected string filepath, got {type(path)}")
        if not path:
            raise ValueError("Filepath cannot be empty")
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {path}")
        if not path.lower().endswith(".pdf"):
            raise ValueError(f"File must be a PDF: {path}")
        if os.path.getsize(path) == 0:
            raise ValueError(f"File is empty: {path}")
        
    doc1 = fitz.open(path1)
    doc1_text = "\n".join(page.get_text() for page in doc1)

    doc2 = fitz.open(path2)
    doc2_text = "\n".join(page.get_text() for page in doc2)
    
    return doc1_text, doc2_text

def construct_zero_shot(document_text: str):
    prompt = f"""You are a security requirements analyst. Analyze the following security requirements document and identify all key data elements (KDEs).
        For each KDE, extract:
        - A concise element name
        - All requirements that map to that element

        Return your response as valid YAML only, with no additional text, in this exact format:
        element1:
        name: <element name>
        requirements:
            - req1
            - req2
        element2:
        name: <element name>
        requirements:
            - req1

        Document:
        {document_text}"""
    return prompt

def construct_few_shot(document_text: str):
    prompt = f"""You are a security requirements analyst. Analyze security requirements documents and identify all key data elements (KDEs). A KDE is a critical piece of data that security controls are built around.

        Here are examples of KDE extraction:

        Example 1:
        Document excerpt: "1.1 Ensure all user accounts have passwords of at least 12 characters. 1.2 Passwords must contain uppercase, lowercase, numbers, and symbols."
        Output:
        element1:
        name: Password Policy
        requirements:
            - Minimum length of 12 characters
            - Must contain uppercase, lowercase, numbers, and symbols

        Example 2:
        Document excerpt: "2.1 All network traffic must be encrypted using TLS 1.2 or higher. 2.2 Unencrypted protocols such as HTTP and FTP are prohibited."
        Output:
        element1:
        name: Network Encryption
        requirements:
            - TLS 1.2 or higher required
            - Unencrypted protocols prohibited

        Now extract KDEs from this document and return valid YAML only, no additional text:
        element1:
        name: <element name>
        requirements:
            - req1

        Document:
        {document_text}"""
    
    return prompt

def construct_cot(document_text: str):
    prompt = f"""You are a security requirements analyst. Your task is to extract key data elements (KDEs) from a security requirements document. A KDE is a critical data entity that one or more security requirements are built around.

        Follow these steps:
        1. Read the document carefully and identify distinct security topics or themes
        2. For each theme, determine if it represents a discrete data entity that security controls protect or govern
        3. Name that entity concisely (e.g., "User Credentials", "Audit Logs", "Network Configuration")
        4. Map every requirement in the document that relates to that entity
        5. Note that one KDE can map to multiple requirements
        6. Format the final output as valid YAML

        Think through each step before producing output. After your reasoning, output the YAML under a line that says "YAML OUTPUT:" with no other text after that line.

        Document:
        {document_text}"""
    return prompt

def extract_kdes(text: str, input_path: str) -> dict:
    """Uses Gemma-3-1B with all three prompts to extract KDEs, saves to YAML, returns last result."""
    PROMPTS = [
    ("zero-shot", construct_zero_shot),
    ("few-shot", construct_few_shot),
    ("chain-of-thought", construct_cot),
    ]
    OUTPUT_DIR = "output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    results = {}
    for prompt_type, prompt_fn in PROMPTS:
        prompt = prompt_fn(text)
        
        messages = [{"role": "user", "content": prompt}]
        output = pipe(messages, max_new_tokens=1000)
        response = output[0][0]['generated_text'][-1]['content']

        try:
            kdes = yaml.safe_load(response)
        except yaml.YAMLError:
            kdes = {}

        output_filename = os.path.join(OUTPUT_DIR, f"{base_name}-kdes.yaml")
        with open(output_filename, "a") as f:
            yaml.dump({prompt_type: kdes}, f, default_flow_style=False)
            f.write("\n")

        collect_output(
            llm_name="google/gemma-3-1b-it",
            prompt=prompt,
            prompt_type=prompt_type,
            llm_output=str(kdes)
        )

        results[prompt_type] = kdes

    return results


def collect_output(llm_name: str, prompt: str, prompt_type: str, llm_output: str, output_file: str = "llm_outputs.txt") -> None:
    """Collects LLM output and appends it to a formatted text file."""
    OUTPUT_DIR = "output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, output_file), "a") as f:
        f.write(f"*LLM Name*\n{llm_name}\n\n")
        f.write(f"*Prompt Used*\n{prompt}\n\n")
        f.write(f"*Prompt Type*\n{prompt_type}\n\n")
        f.write(f"*LLM Output*\n{llm_output}\n\n")
        f.write("="*50 + "\n\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <path1> <path2>")
        sys.exit(1)

    path1 = sys.argv[1]
    path2 = sys.argv[2]

    OUTPUT_DIR = "output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    open(os.path.join(OUTPUT_DIR, "llm_outputs.txt"), "w").close()

    text1, text2 = load_documents(path1, path2)

    kdes1 = extract_kdes(text1, path1)
    kdes2 = extract_kdes(text2, path2)