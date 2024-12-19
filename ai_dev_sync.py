import os
import glob
import json
import logging
import time
import requests
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
API_KEY_ENV_VAR = "GEMINI_API_KEY"

# Function to read API key from environment
def get_api_key() -> str:
    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        raise ValueError(f"Environment variable {API_KEY_ENV_VAR} is not set.")
    return api_key

# Function to recursively search for files matching patterns
def find_files(base_path: str, patterns: List[str]) -> List[str]:
    matched_files = []
    for pattern in patterns:
        matched_files.extend(glob.glob(os.path.join(base_path, pattern), recursive=True))
    return matched_files

# Function to read file contents
def read_files(file_paths: List[str]) -> List[dict]:
    contents = []
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                contents.append({"filename": file_path, "content": file.read()})
                logger.info(f"Read content from {file_path}")
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
    return contents

# Function to send request to the API
def send_request(prompt: str) -> dict:
    api_key = get_api_key()
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    logger.info(f"Sending API request: {json.dumps(payload, indent=2)}")

    response = requests.post(f"{API_URL}?key={api_key}", headers=headers, json=payload)

    logger.info(f"API Response: {response.text}")

    if response.status_code != 200:
        raise RuntimeError(f"API request failed with status code {response.status_code}: {response.text}")

    return response.json()

# Function to process response and update/create files
def process_response(response: dict, base_path: str):
    for content in response.get("contents", []):
        filename = content.get("filename")
        file_content = content.get("text")

        if not filename or not file_content:
            logger.warning("Invalid content in response: missing filename or text.")
            continue

        file_path = os.path.join(base_path, filename)
        try:
            if os.path.exists(file_path):
                logger.info(f"Updating existing file: {file_path}")
            else:
                logger.info(f"Creating new file: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(file_content)
        except Exception as e:
            logger.error(f"Failed to write to {file_path}: {e}")

# Main function to process prompt
def process_prompt(prompt: str, base_path: str, patterns: List[str]):
    logger.info(f"Processing prompt: {prompt}")

    # Search for files and integrate contents into prompt
    file_paths = find_files(base_path, patterns)
    logger.info(f"Found files: {file_paths}")

    file_contents = read_files(file_paths)
    for file in file_contents:
        prompt += f"\n\nFile: {file['filename']}\n{file['content']}"

    # Send prompt to API
    logger.info("Waiting for API response...")
    response = send_request(prompt)

    # Process API response
    process_response(response, base_path)

# Test case
if __name__ == "__main__":
    try:
        test_prompt = "Erstelle eine betriebshandbuch"
        base_path = "/home/andre/IdeaProjects/algosec-connector"
        patterns = ["src/**/*.java", "*"]

        process_prompt(test_prompt, base_path, patterns)
    except Exception as e:
        logger.error(f"Error during processing: {e}")
