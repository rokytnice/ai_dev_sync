import os
import json
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def send_prompt(prompt):
    """
    Sends a prompt to the API and returns the response.
    """
    url = f"{BASE_URL}?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    logging.debug(f"Sending request: {json.dumps(payload, indent=2)}")
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    logging.debug(f"Received response: {response.text}")
    return response.json()


def search_files_in_path(path, filenames=None):
    """
    Recursively searches for files in a given path and optionally checks for specific filenames.
    """
    matching_files = {}

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)

            if filenames is None or file in filenames:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        matching_files[file] = f.read()
                        logging.info(f"File found and read: {file_path}")
                except UnicodeDecodeError:
                    logging.warning(f"Failed to read file {file_path} with UTF-8 encoding. Trying binary mode.")
                    with open(file_path, 'rb') as f:
                        matching_files[file] = f.read().decode('latin1', errors='ignore')
                        logging.info(f"File read with fallback encoding: {file_path}")

    return matching_files


def extend_prompt_with_files(prompt, path, filenames=None):
    """
    Extends the given prompt by including the content of files found in the path.
    """
    file_contents = search_files_in_path(path, filenames)

    for filename, content in file_contents.items():
        prompt += f"\n\n--- File: {filename} ---\n{content}"

    return prompt


def update_or_create_files(path, filenames_with_contents):
    """
    Updates or creates files based on the given content.
    """
    for filename, content in filenames_with_contents.items():
        file_path = os.path.join(path, filename)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            f.write(content)
            logging.info(f"File updated or created: {file_path}")


def main():
    """
    Main function for executing the program.
    """
    working_directory = "/home/andre/IdeaProjects/algosec-connector"
    initial_prompt = "Erstelle mir einen Betriebshandbuch"

    # Extend prompt with all files in the directory
    prompt = extend_prompt_with_files(initial_prompt, working_directory)

    # Send the prompt to the API
    response = send_prompt(prompt)

    # Process the response
    body = response.get("contents", [])
    filenames_with_contents = {}

    for content in body:
        if 'parts' in content:
            for part in content['parts']:
                if 'text' in part:
                    filename = part.get("filename", "response_output.txt")
                    filenames_with_contents[filename] = part['text']

    # Update or create files with the response content
    update_or_create_files(working_directory, filenames_with_contents)

    # Print formatted response text to console
    for content in body:
        for part in content.get("parts", []):
            if "text" in part:
                formatted_text = part["text"].replace("\\n", "\n")
                print("\nFormatted Text Response:\n")
                print(formatted_text)


if __name__ == "__main__":
    main()
