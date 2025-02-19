import subprocess
import os
import requests
import json
import re


def extract_java_code(response_json: dict) -> str:
    try:
        content_parts = response_json["candidates"][0]["content"]["parts"]
        if isinstance(content_parts, list) and len(content_parts) > 0:
            response_text = content_parts[0].get("text", "")
            match = re.search(r'```java\n(.*?)```', response_text, re.DOTALL)
            return match.group(1).strip() if match else response_text.strip()
    except (KeyError, IndexError, AttributeError):
        print("Fehler: Unerwartete API-Antwortstruktur.")
    return ""


def extract_package_name(java_code: str) -> str:
    match = re.search(r'package\s+([a-zA-Z0-9_.]+);', java_code)
    return match.group(1) if match else ""


def find_java_class(directory: str, class_name: str) -> str:
    print(f"Suche nach der Java-Klasse {class_name} in {directory}...")
    expected_filename = f"{class_name}.java"

    for root, _, files in os.walk(directory):
        print(f"Durchsuche Verzeichnis: {root}")
        for file in files:
            if file == "Application.java":
                continue
        if file == expected_filename:
            java_file_path = os.path.join(root, file)
            print(f"Java-Klasse gefunden: {java_file_path}")
            return java_file_path

    print(f"Klasse {class_name} nicht gefunden.")
    return ""


def call_ai_agent(source_code: str, api_key: str, error_message: str = "") -> str:
    package_name = extract_package_name(source_code)
    prompt = f"Erstelle eine JUnit-Testklasse für den folgenden Java-Code mit der folgenden Package-Deklaration: package {package_name};\n{source_code}"
    if error_message:
        prompt += f"\n\nDer vorherige Code hatte einen Kompilierungsfehler: {error_message}. Bitte repariere ihn."

    print(f"Sende Quellcode an AI-Agent zur Verarbeitung...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    print("--- API Request ---")
    print(json.dumps(data, indent=2))

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        response_json = response.json()
    except requests.Timeout:
        print("Fehler: Die Anfrage an die API hat das Zeitlimit überschritten.")
        return ""
    except requests.RequestException as e:
        print(f"Fehler: API-Anfrage fehlgeschlagen - {e}")
        return ""

    print("--- API Response ---")
    print(json.dumps(response_json, indent=2))

    return extract_java_code(response_json)


def save_test_class(project_dir: str, test_code: str, class_name: str):
    package_name = extract_package_name(test_code)
    test_dir = os.path.join(project_dir, "src", "test", "java")

    if package_name:
        package_path = package_name.replace(".", os.sep)
        test_dir = os.path.join(test_dir, package_path)

    if not os.path.isdir(test_dir):
        os.makedirs(test_dir)

    test_file_path = os.path.join(test_dir, f"{class_name}Test.java")
    print(f"Speichere Testklasse: {test_file_path}")

    if os.path.exists(test_file_path):
        print("Testklasse existiert bereits. Erweitere bestehende Klasse...")
        with open(test_file_path, "r", encoding="utf-8") as test_file:
            existing_code = test_file.read()

        new_code = existing_code + "\n\n" + test_code
    else:
        new_code = test_code

    with open(test_file_path, "w", encoding="utf-8") as test_file:
        test_file.write(new_code)
    print(f"Testklasse gespeichert: {test_file_path}")
    return test_file_path


def run_gradle_test(project_dir: str, package_name: str, class_name: str):
    gradle_executable = os.path.join(project_dir, "gradlew.bat" if os.name == "nt" else "gradlew")

    if not os.path.isfile(gradle_executable):
        print(f"Fehler: Gradle Wrapper nicht gefunden im Verzeichnis {project_dir}.")
        return False

    test_class = f"{package_name}.{class_name}Test"
    gradle_command = [gradle_executable, "test", "--tests", test_class]
    print(f"Führe Test aus: {' '.join(gradle_command)}")

    try:
        result = subprocess.run(gradle_command, cwd=project_dir, text=True, capture_output=True, check=True)
        print("Tests erfolgreich ausgeführt!")
        return True
    except subprocess.CalledProcessError as e:
        print("Fehler beim Ausführen der Tests:")
        print(e.stderr)
        return False


if __name__ == "__main__":
    projektpfad = os.getenv("GRADLE_PROJECT_PATH")
    api_key = os.getenv("API_KEY")

    if not projektpfad or not api_key:
        print("Fehler: Bitte setze die Umgebungsvariablen GRADLE_PROJECT_PATH und API_KEY.")
    else:
        java_source_path = os.path.join(projektpfad, "src", "main")
        for root, _, files in os.walk(java_source_path):
            for file in files:
                if file.endswith(".java"):
                    class_name = file[:-5]
                    java_file_path = os.path.join(root, file)
                    print(f"Lese Datei: {java_file_path}")
                    with open(java_file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                    test_code = call_ai_agent(source_code, api_key)
                    if test_code:
                        package_name = extract_package_name(test_code)
                        test_file_path = save_test_class(projektpfad, test_code, class_name)
                        if run_gradle_test(projektpfad, package_name, class_name):
                            print(f"Test für {class_name} erfolgreich.")
                        else:
                            print(f"Test für {class_name} fehlgeschlagen. Prozess wird gestoppt.")
                            break
