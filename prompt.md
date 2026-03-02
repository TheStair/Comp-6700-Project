# Prompts

## Zero Shot
You are a security requirements analyst. Analyze the following security requirements document and identify all key data elements (KDEs).

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
{document_text}

## Few-Shot
You are a security requirements analyst. Analyze security requirements documents and identify all key data elements (KDEs). A KDE is a critical piece of data that security controls are built around.

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
{document_text}


## Chain of Thought
You are a security requirements analyst. Your task is to extract key data elements (KDEs) from a security requirements document. A KDE is a critical data entity that one or more security requirements are built around.

Follow these steps:
1. Read the document carefully and identify distinct security topics or themes
2. For each theme, determine if it represents a discrete data entity that security controls protect or govern
3. Name that entity concisely (e.g., "User Credentials", "Audit Logs", "Network Configuration")
4. Map every requirement in the document that relates to that entity
5. Note that one KDE can map to multiple requirements
6. Format the final output as valid YAML

Think through each step before producing output. After your reasoning, output the YAML under a line that says "YAML OUTPUT:" with no other text after that line.

Document:
{document_text}