import os
import json
import logging
import requests
import itertools
import sys
import time
from pathlib import Path
from typing import List, Dict
from threading import Thread

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send_prompt(self, prompt: str) -> Dict:
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        logging.info(f"Sending API request with payload: {json.dumps(payload)}")
        logging.info(f"RAW REQUEST: {json.dumps(payload)}")
        response_container = {}
        progress_thread = Thread(target=self._show_progress, args=(response_container,))
        progress_thread.start()
        try:
            response = requests.post(f"{API_URL}?key={self.api_key}", headers=headers, json=payload)
            response.raise_for_status()
            response_container['done'] = True
            logging.info(f"Received API response: {response.text}")
            logging.info(f"RAW RESPONSE: {response.text}")
            return response.json()
        finally:
            progress_thread.join()

    def _show_progress(self, response_container):
        dots = itertools.cycle(['.', '..', '...'])
        while not response_container.get('done'):
            logging.info(f"Waiting for API response {next(dots)}")
            time.sleep(0.5)

class FileManager:
    def __init__(self, base_directory: Path):
        self.base_directory = base_directory

    def find_files(self, patterns: List[str]) -> List[Path]:
        files = list(self.base_directory.rglob("*"))
        filtered_files = []
        for pattern in patterns:
            filtered_files.extend([f for f in files if f.match(pattern)])
        logging.info(f"Filtered files: {filtered_files}")
        return filtered_files

    def read_file_content(self, file_path: Path) -> str:
        logging.info(f"Reading content from file: {file_path}")
        return file_path.read_text(encoding='utf-8')

class PromptProcessor:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    def build_prompt_for_file(self, base_prompt: str, file: Path) -> str:
        content = self.file_manager.read_file_content(file)
        prompt = f"{base_prompt}\n\n---\n{file}:{content}"
        logging.info(f"Constructed prompt for file {file}: {prompt}")
        return prompt

class ResponseHandler:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.collected_responses = []

    def process_response(self, response: Dict):
        candidates = response.get("candidates", [])
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                self.collected_responses.append(part["text"])
                self.extract_and_update_java_files(part["text"])

    def extract_and_update_java_files(self, text: str):
        start_tag = "```java"
        end_tag = "```"
        while start_tag in text:
            start = text.find(start_tag) + len(start_tag)
            end = text.find(end_tag, start)
            if end == -1:
                break
            java_content = text[start:end].strip()
            text = text[end + len(end_tag):]  # Continue with the remaining text
            self.update_files(java_content)

    def update_files(self, content: str):
        lines = content.splitlines()
        if lines:
            package_line = next((line for line in lines if line.startswith("package ")), None)
            class_name_line = next((line for line in lines if line.startswith("public class") or line.startswith("public enum")), None)
            if not class_name_line:
                logging.error("Class or enum name not found in the provided content.")
                return

            class_name = class_name_line.split()[2].split("{")[0].strip()
            file_name = f"{class_name}.java"
            file_content = "\n".join(lines)

            if package_line:
                package_path = package_line.replace("package", "").replace(";", "").strip().replace(".", "/")
                package_path = package_path.lstrip("/")  # Ensure no leading slash
                if self.file_manager.base_directory.as_posix().endswith(package_path):
                    file_path = self.file_manager.base_directory / file_name
                else:
                    file_path = self.file_manager.base_directory / package_path / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(file_content, encoding='utf-8')
                logging.info(f"Updated file: {file_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    base_prompt = ("füge javadoc hinzu ")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("API key is missing. Set GEMINI_API_KEY as an environment variable.")

    base_directory = Path("/home/andre/IdeaProjects/algosec-connector/src/main/java/fwat/application/security/logging")
    file_manager = FileManager(base_directory)
    prompt_processor = PromptProcessor(file_manager)
    api_client = APIClient(api_key)
    response_handler = ResponseHandler(file_manager)

    patterns = ["*.java", "*.conf", "*.properties", "*.yml"]

    files = file_manager.find_files(patterns)
    for file in files:
        prompt = prompt_processor.build_prompt_for_file(base_prompt, file)
        try:
            response = api_client.send_prompt(prompt)
            response_handler.process_response(response)
            time.sleep(4)  # Rate limiting: Wait for 4 seconds between requests
        except Exception as e:
            logging.error(f"Error occurred while processing file {file}: {e}")

    # Combine and output all collected responses
    combined_responses = "\n\n".join(response_handler.collected_responses)
    logging.info("\n--- Combined Responses ---\n")
    logging.info(combined_responses)
