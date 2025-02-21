#!/usr/bin/env python3
import os
import sys
import logging
import subprocess
import requests
import json
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# =============================================================================
# Globale Einstellungen
# =============================================================================

DEFAULT_GRADLE_COMMAND = "gradlew"  # Name des Gradle-Wrapper-Skripts
MAIN_SRC_DIR = os.path.join("src", "main")  # Verzeichnis mit Quellcode
TEST_SRC_DIR = os.path.join("src", "test", "java")  # Verzeichnis für Testklassen


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def get_project_dir():
    """
    Liest das Projektverzeichnis aus der Umgebungsvariable PROJECT_DIR.
    Falls nichts vorhanden ist, wird interaktiv vom Nutzer ein Pfad abgefragt.
    """
    project_dir = os.environ.get("PROJECT_DIR")
    if not project_dir:
        project_dir = input("Bitte gib den Pfad zum Projektverzeichnis an: ").strip()
    if not project_dir:
        logging.error("Kein Projektverzeichnis angegeben.")
        sys.exit(1)
    # Absoluten Pfad erzeugen
    project_dir = os.path.abspath(project_dir)
    return project_dir


def get_api_key():
    """
    Liest den API-Key aus der Umgebungsvariable API_KEY.
    Falls nichts vorhanden ist, wird das Skript abgebrochen.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        logging.error("API_KEY ist nicht gesetzt. Bitte Umgebungsvariable setzen.")
        sys.exit(1)
    return api_key


def prompt_for_class_name():
    """
    Fragt den Nutzer nach dem Namen einer Java-Klasse.
    Gibt einen leeren String zurück, wenn keine Eingabe erfolgt ist.
    """
    class_name = input("Gib den Namen der Java-Klasse an (Enter für alle Klassen): ").strip()
    return class_name


def find_java_files(base_dir, filter_class_name=None):
    """
    Durchsucht rekursiv das base_dir nach .java-Dateien.
    - filter_class_name: wenn angegeben, wird nur die Datei zurückgegeben,
      deren Dateiname (ohne .java) mit filter_class_name übereinstimmt.
    - Schließt Dateien aus, die 'Application.java' heißen.

    Gibt eine Liste (Pfade) zurück.
    """
    matches = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".java"):
                if file == "Application.java":
                    # "Application" nicht testen
                    continue
                full_path = os.path.join(root, file)
                if filter_class_name:
                    # Nur die Datei mit passendem Klassennamen
                    if os.path.splitext(file)[0] == filter_class_name:
                        matches.append(full_path)
                else:
                    # Alle
                    matches.append(full_path)
    return matches


def read_file_content(file_path):
    """
    Liest den Inhalt einer Datei und gibt ihn als String zurück.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def call_llm(api_key, prompt_text):
    """
    Ruft das LLM über die angegebene REST-Schnittstelle auf.
    Gibt den generierten Text zurück, oder None bei Fehlern.

    Timeout = 30 Sekunden
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{
            "parts": [
                {
                    "text": prompt_text
                }
            ]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        # Hier musst du je nach Struktur der Antwort anpassen:
        # Annahme: Die generierte Antwort steckt in data["contents"][0]["parts"][0]["text"]
        # -> Die genaue Struktur kann variieren. Prüfe ggf. die tatsächliche Response!

        # Mögliche Beispielstruktur:
        # {
        #   "contents": [
        #       {
        #           "parts": [
        #               {
        #                   "text": "... Test-Klasse ..."
        #               }
        #           ]
        #       }
        #   ]
        # }

        if "contents" in data and len(data["contents"]) > 0:
            if "parts" in data["contents"][0] and len(data["contents"][0]["parts"]) > 0:
                return data["contents"][0]["parts"][0].get("text", "")

        logging.warning("Unerwartete Antwortstruktur vom LLM: %s", data)
        return None
    except requests.exceptions.Timeout:
        logging.error("Timeout: Die API hat nicht innerhalb von 30s geantwortet.")
    except requests.exceptions.RequestException as e:
        logging.error("Fehler bei der Anfrage an das LLM: %s", e)

    return None


def extract_package_and_class_name(test_code):
    """
    Versucht aus dem generierten Testcode die Package-Angabe und den Klassennamen zu extrahieren.
    Gibt (package, class_name) zurück.

    Beispiel:
        package com.example.tests;
        public class MyClassTest { ... }
    """
    # Ggf. reguläre Ausdrücke verwenden
    import re

    package_pattern = r'^\s*package\s+([a-zA-Z0-9_.]+)\s*;\s*'
    class_pattern = r'public\s+class\s+([A-Za-z0-9_]+)\s*'

    package_match = re.search(package_pattern, test_code, re.MULTILINE)
    class_match = re.search(class_pattern, test_code)

    pkg = package_match.group(1) if package_match else None
    cls = class_match.group(1) if class_match else None

    return pkg, cls


def build_test_filepath(project_dir, package_name, class_name):
    """
    Baut den Pfad zur Testklasse anhand des package-Namens und Klassen-Namens.
    Beispiel: src/test/java/com/example/MyClassTest.java
    """
    package_path = os.path.join(project_dir, TEST_SRC_DIR, *package_name.split('.'))
    os.makedirs(package_path, exist_ok=True)
    test_class_path = os.path.join(package_path, f"{class_name}.java")
    return test_class_path


def merge_test_code(existing_code, new_code):
    """
    Falls bereits eine Testklasse existiert, wird sie erweitert.
    Ein einfacher Ansatz:
      1. Entferne abschließende '}' aus dem existing_code
      2. Füge Methoden aus new_code hinzu
      3. Schließe mit '}' ab

    *Achtung:* Dieser einfache Ansatz kann zu Konflikten führen, wenn
    das generierte Codegerüst sich zu sehr von der vorhandenen Klasse unterscheidet.
    In komplexen Fällen müsste man z.B. AST-Parsing vornehmen.
    """
    # Extrahiere alles außer das letzte '}' aus existing_code
    import re

    # Falls das existing_code bereits mit '}' endet:
    match = re.search(r'(.*)\}\s*$', existing_code, re.DOTALL)
    if match:
        existing_without_brace = match.group(1)
    else:
        # Falls keine geschweifte Klammer am Ende vorhanden, nimm den Code, wie er ist
        existing_without_brace = existing_code

    # Nun aus dem new_code nur den Inhalt *innerhalb* der Klasse übernehmen
    # (d.h. Zeilen zwischen `public class X {` und der letzten `}`).
    # Hier sehr einfach gelöst, z.B. per Regex oder manueller Suche.
    class_body_pattern = r'public\s+class\s+[A-Za-z0-9_]+\s*\{(.*)\}\s*$'
    body_match = re.search(class_body_pattern, new_code, re.DOTALL)
    if body_match:
        new_body = body_match.group(1).strip()
    else:
        # Falls kein Treffer, nehmen wir den gesamten new_code – grob
        new_body = new_code

    # Zusammenführen
    merged = existing_without_brace.rstrip() + "\n\n" + "    // --- Erweiterter Testcode ---\n" + new_body + "\n}"
    return merged


def write_test_code(test_file_path, code):
    """
    Schreibt den Test-Code in die angegebene Datei.
    """
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    logging.info("Testklasse geschrieben: %s", test_file_path)


def run_gradle_test(project_dir, package_name, test_class_name):
    """
    Führt den Gradle-Test nur für die angegebene Testklasse aus:
        ./gradlew test --tests <packageName>.<testClassName>
    Gibt die Ausgabe (stdout + stderr) zurück.
    Falls ein Fehler bei Gradle auftritt, wird eine Exception geworfen.
    """
    gradlew_path = os.path.join(project_dir, DEFAULT_GRADLE_COMMAND)
    if os.name == 'nt':
        gradlew_cmd = [gradlew_path + ".bat"]  # Windows
    else:
        gradlew_cmd = [gradlew_path]  # Unix/Mac

    full_class_name = f"{package_name}.{test_class_name}"
    cmd = gradlew_cmd + ["test", "--tests", full_class_name]

    logging.info("Führe Gradle-Test aus: %s", " ".join(cmd))

    # Subprozess ausführen
    result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

    # Logging
    logging.info("Gradle-Ausgabe:\n%s", result.stdout)
    if result.stderr:
        logging.error("Gradle-Fehlerausgabe:\n%s", result.stderr)

    return_code = result.returncode

    if return_code != 0:
        logging.error("Gradle hat Fehler zurückgegeben (returncode=%s).", return_code)

    return result.stdout + "\n" + result.stderr, return_code


def detect_compile_error(gradle_output):
    """
    Sucht in der Gradle-Ausgabe nach Hinweisen auf Kompilierungsfehler.
    Dies kann je nach Gradle-Version/Plugin variieren.
    Ein einfacher Ansatz: Suche nach "Compilation failed" oder "cannot find symbol" etc.
    """
    keywords = ["Compilation failed", "cannot find symbol", "error:", "compilation error"]
    lower_out = gradle_output.lower()
    for kw in keywords:
        if kw.lower() in lower_out:
            return True
    return False


def create_prompt_for_test_generation(java_source):
    """
    Erstellt den Prompt, der an das LLM gesendet wird, um Testcode zu generieren.
    """
    prompt = f"Generiere Testcode für die folgende Java-Klasse:\n\n{java_source}"
    return prompt


def create_prompt_for_fix(compile_error_msg, current_test_code):
    """
    Erstellt den Prompt, um den Testcode zu reparieren.
    """
    prompt = (
        "Der folgende Testcode kompiliert nicht. "
        "Hier ist die Fehlermeldung:\n"
        f"{compile_error_msg}\n\n"
        "Bitte repariere den Testcode:\n\n"
        f"{current_test_code}"
    )
    return prompt


# =============================================================================
# Hauptablauf
# =============================================================================

def main():
    project_dir = get_project_dir()
    api_key = get_api_key()

    class_name_input = prompt_for_class_name()

    # Java-Dateien finden
    main_src_path = os.path.join(project_dir, MAIN_SRC_DIR)
    java_files = find_java_files(main_src_path, filter_class_name=class_name_input if class_name_input else None)

    # Wenn class_name_input gesetzt wurde, aber keine Datei gefunden -> Abbruch
    if class_name_input and not java_files:
        logging.error("Keine Datei mit dem Namen '%s.java' gefunden.", class_name_input)
        sys.exit(1)

    # Falls keine Klasse angegeben ist, aber `java_files` leer -> nichts zu tun
    if not java_files:
        logging.info("Keine Java-Dateien gefunden.")
        sys.exit(0)

    # Wir verarbeiten jede gefundene Java-Datei
    for java_file in java_files:
        # Schritt 1: Quelle lesen
        logging.info("Lese Java-Klasse: %s", java_file)
        source_code = read_file_content(java_file)

        # Prompt erstellen
        prompt_text = create_prompt_for_test_generation(source_code)

        # LLM aufrufen
        logging.info("Sende Quellcode an LLM für Testcode-Generierung...")
        generated_code = call_llm(api_key, prompt_text)
        if not generated_code:
            logging.error("Keine Testcode-Antwort erhalten. Überspringe Datei %s.", java_file)
            continue

        # Paket & Klassenname extrahieren
        package_name, test_class_name = extract_package_and_class_name(generated_code)
        if not package_name or not test_class_name:
            logging.warning("Konnte package oder class name aus generiertem Testcode nicht extrahieren. "
                            "Überspringe Datei %s.", java_file)
            continue

        # Test-Dateipfad bestimmen
        test_file_path = build_test_filepath(project_dir, package_name, test_class_name)

        # Wenn die Testklasse bereits existiert -> Mergen
        if os.path.exists(test_file_path):
            logging.info("Testklasse existiert bereits, erweitere sie: %s", test_file_path)
            existing_test_code = read_file_content(test_file_path)
            merged_code = merge_test_code(existing_test_code, generated_code)
            write_test_code(test_file_path, merged_code)
        else:
            # Neu anlegen
            write_test_code(test_file_path, generated_code)

        # Test ausführen
        gradle_output, return_code = run_gradle_test(project_dir, package_name, test_class_name)

        # Wenn Kompilierungsfehler -> LLM auffordern, Code zu reparieren
        if return_code != 0 and detect_compile_error(gradle_output):
            logging.info("Kompilierungsfehler erkannt. Sende Fehlermeldung an LLM zum Reparieren...")
            # Erstelle Prompt zum Fix
            current_test_code = read_file_content(test_file_path)
            fix_prompt = create_prompt_for_fix(gradle_output, current_test_code)

            fixed_code = call_llm(api_key, fix_prompt)
            if fixed_code:
                # Testklasse erneut schreiben
                logging.info("Erhalte reparierten Testcode und speichere.")
                write_test_code(test_file_path, fixed_code)

                # Nochmal Gradle-Test ausführen
                gradle_output, return_code = run_gradle_test(project_dir, package_name, test_class_name)
                if return_code != 0 and detect_compile_error(gradle_output):
                    logging.error("Auch der reparierte Testcode schlägt fehl. "
                                  "Fahre mit der nächsten Klasse fort.")
                else:
                    logging.info("Reparierter Testcode kompiliert und läuft erfolgreich.")
            else:
                logging.error("Keine reparierte Version vom LLM erhalten.")
        else:
            if return_code == 0:
                logging.info("Test erfolgreich für Klasse: %s", test_class_name)
            else:
                logging.info("Test fehlgeschlagen (kein Kompilierungsfehler, ggf. Assertion-Fehler).")

    logging.info("Alle Klassen wurden bearbeitet.")


if __name__ == "__main__":
    main()
