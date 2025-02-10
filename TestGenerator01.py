import subprocess
import os
import requests
import json
import re


def extract_java_code(response_text: str) -> str:
    """
    Extrahiert den Java-Code aus einem Markdown-Codeblock (```java ... ```)
    """
    match = re.search(r'```java\n(.*?)```', response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_text.strip()


def call_ai_agent(source_code: str, api_key: str) -> str:
    """
    Sendet den Quellcode an die AI-Schnittstelle und erhält eine generierte Testklasse.
    :param source_code: Der Quellcode der Java-Klasse.
    :param api_key: Der API-Schlüssel für den LLM-Dienst.
    :return: Der generierte Testcode als String oder eine Fehlermeldung.
    """
    print(f"Sende Quellcode an AI-Agent zur Verarbeitung...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": f"Erstelle eine JUnit-Testklasse für den folgenden Java-Code:\n{source_code}"}]
        }]
    }

    print("--- API Request ---")
    print(json.dumps(data, indent=2))

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()

    print("--- API Response ---")
    print(json.dumps(response_json, indent=2))

    if "candidates" not in response_json or not response_json["candidates"]:
        print("Fehler: Unerwartete API-Antwort erhalten.")
        return ""

    content = response_json["candidates"][0].get("content", "")
    if not isinstance(content, str):
        print("Fehler: API-Antwort enthält kein gültiges Textformat.")
        return ""

    return extract_java_code(content)


def save_test_class(project_dir: str, test_code: str, class_name: str):
    """
    Speichert die generierte Testklasse im src/test Verzeichnis.
    """
    test_dir = os.path.join(project_dir, "src", "test")
    if not os.path.isdir(test_dir):
        os.makedirs(test_dir)

    test_file_path = os.path.join(test_dir, f"{class_name}Test.java")
    print(f"Speichere Testklasse: {test_file_path}")

    with open(test_file_path, "w", encoding="utf-8") as test_file:
        test_file.write(test_code)
    print(f"Testklasse gespeichert: {test_file_path}")


def find_java_class(directory: str, class_name: str):
    """
    Sucht rekursiv nach einer Java-Klasse im Verzeichnis und loggt die durchsuchten Verzeichnisse und Dateien.
    """
    # print(f"Suche nach der Java-Klasse {class_name} in {directory}...")
    expected_filename = f"{class_name}.java"
    for root, _, files in os.walk(directory):
        # print(f"Durchsuche Verzeichnis: {root}")
        for file in files:
            print(f"Gefundene Datei: {file}")
            if file.strip() == expected_filename.strip():
                java_file_path = os.path.join(root, file)
                print(f"Java-Klasse gefunden: {java_file_path}")
                return java_file_path
            else:
                print(f"Dateiname stimmt nicht genau überein: Erwartet '{expected_filename}', gefunden '{file}'")
    print("Klasse nicht gefunden.")
    return None


def run_gradle_tests(project_dir: str):
    """
    Führt die Java-Tests in einem Gradle-Projekt aus.
    """
    gradle_executable = os.path.join(project_dir, "gradlew.bat" if os.name == "nt" else "gradlew")

    if not os.path.isfile(gradle_executable):
        print(f"Fehler: Gradle Wrapper nicht gefunden im Verzeichnis {project_dir}.")
        return

    gradle_command = [gradle_executable, "test"]
    print(f"Führe Kommando aus: {' '.join(gradle_command)}")

    try:
        result = subprocess.run(gradle_command, cwd=project_dir, text=True, capture_output=True, check=True)
        print("Tests erfolgreich ausgeführt!\n")
        print("--- Ausgabe ---")
        print(result.stdout)
        print("--- Fehler (falls vorhanden) ---")
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print("Fehler beim Ausführen der Tests:\n")
        print("--- Ausgabe ---")
        print(e.stdout)
        print("--- Fehler ---")
        print(e.stderr)


if __name__ == "__main__":
    projektpfad = os.getenv("GRADLE_PROJECT_PATH")
    api_key = os.getenv("API_KEY")

    if not projektpfad or not api_key:
        print("Fehler: Bitte setze die Umgebungsvariablen GRADLE_PROJECT_PATH und API_KEY.")
    else:
        java_class_name = input("Gib den Namen der Java-Klasse ein: ").strip()

        if java_class_name:
            java_source_path = os.path.join(projektpfad, "src", "main")
            java_file_path = find_java_class(java_source_path, java_class_name)

            if java_file_path:
                print(f"Lese Datei: {java_file_path}")
                with open(java_file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                test_code = call_ai_agent(source_code, api_key)
                if test_code:
                    save_test_class(projektpfad, test_code, java_class_name)
                    run_gradle_tests(projektpfad)
            else:
                print(f"Die Java-Klasse {java_class_name} wurde nicht gefunden.")
