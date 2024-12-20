import os
import json
import logging
import requests
import difflib
import itertools
import sys
import time
from pathlib import Path
from typing import List, Dict
from threading import Thread

# Konfiguration für Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

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
        response_container = {}
        progress_thread = Thread(target=self._show_progress, args=(response_container,))
        progress_thread.start()
        try:
            response = requests.post(f"{API_URL}?key={self.api_key}", headers=headers, json=payload)
            response.raise_for_status()
            response_container['done'] = True
            logging.info(f"Received API response: {response.text}")
            return response.json()
        finally:
            progress_thread.join()

    def _show_progress(self, response_container):
        sys.stdout.write("Waiting for API response ")
        sys.stdout.flush()
        dots = itertools.cycle(['.', '..', '...'])
        while not response_container.get('done'):
            sys.stdout.write(next(dots))
            sys.stdout.flush()
            time.sleep(0.5)
            sys.stdout.write('\b' * len(next(dots)))
        sys.stdout.write("\n")

class FileManager:
    def __init__(self, base_directory: Path):
        self.base_directory = base_directory

    def find_files(self, patterns: List[str]) -> List[Path]:
        files = []
        for pattern in patterns:
            files.extend(self.base_directory.rglob(pattern))
        logging.info(f"Files matching patterns {patterns}: {files}")
        return files

    def read_file_content(self, file_path: Path) -> str:
        logging.info(f"Reading content from file: {file_path}")
        return file_path.read_text(encoding='utf-8')

    def write_file_content(self, file_path: Path, content: str):
        if not file_path.parent.exists():
            logging.info(f"Creating directories for path: {file_path.parent}")
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                logging.error(f"Permission denied when creating directory {file_path.parent}: {e}")
                return
        old_content = file_path.read_text(encoding='utf-8') if file_path.exists() else ""
        file_path.write_text(content, encoding='utf-8')
        logging.info(f"File written: {file_path}")
        self.log_diff(file_path, old_content, content)

    def log_diff(self, file_path: Path, old_content: str, new_content: str):
        if old_content != new_content:
            logging.info(f"Changes in file {file_path}:")
            diff = difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                fromfile="Old Content",
                tofile="New Content",
                lineterm=""
            )
            for line in diff:
                logging.info(line)

    def log_file_activity(self, action: str, file_path: Path):
        logging.info(f"File {action}: {file_path}")

    def find_existing_or_new_path(self, package_path: str, file_name: str) -> Path:
        existing_files = self.find_files([f"{package_path}/{file_name}"])
        if existing_files:
            logging.info(f"Existing file found for {file_name}: {existing_files[0]}")
            return existing_files[0]
        else:
            new_path = self.base_directory / package_path / file_name
            logging.info(f"No existing file found. New path created: {new_path}")
            return new_path

class PromptProcessor:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    def build_prompt(self, base_prompt: str, paths: List[Path], patterns: List[str] = ["*"]) -> str:
        prompt = base_prompt
        for path in paths:
            if path.is_dir():
                files = self.file_manager.find_files(patterns)
                for file in files:
                    content = self.file_manager.read_file_content(file)
                    self.file_manager.log_file_activity("read", file)
                    prompt += f"\n\n---\n{file}:{content}"  # Dateiinhalt hinzufügen
            elif path.is_file():
                content = self.file_manager.read_file_content(path)
                self.file_manager.log_file_activity("read", path)
                prompt += f"\n\n---\n{path}:{content}"
        logging.info(f"Constructed prompt: {prompt}")
        return prompt

class ResponseHandler:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    def process_response(self, response: Dict):
        candidates = response.get("candidates", [])
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
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

            # Process the extracted Java content
            self.update_files(java_content)

    def update_files(self, content: str):
        # Extract package name and file content
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
                file_path = self.file_manager.find_existing_or_new_path(package_path, file_name)
                self.file_manager.write_file_content(file_path, file_content)
                self.file_manager.log_file_activity("updated", file_path)




# Hauptprogramm
if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("API key is missing. Set GEMINI_API_KEY as an environment variable.")

    base_directory = Path("/home/andre/IdeaProjects/algosec-connector/")
    file_manager = FileManager(base_directory)
    prompt_processor = PromptProcessor(file_manager)
    api_client = APIClient(api_key)
    response_handler = ResponseHandler(file_manager)

    # Beispiel-Aufruf
    paths = [base_directory]
    base_prompt = ("Aktualisiere alle Java klassen "
                   "Füge einen Error Code hinzu dieser soll technisch ein enum sein und zentral verwaltet werden "
                   "der Error Code soll Teil des error Logstatments sein.")
    patterns = ["*.java"]  # Beispiel für Glob-Muster

    constructed_prompt = prompt_processor.build_prompt(base_prompt, paths, patterns)
    try:
        response = api_client.send_prompt(constructed_prompt)
        response_handler.process_response(response)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
