import subprocess
import os


def run_gradle_tests(project_dir: str):
    """
    Führt die Java-Tests in einem Gradle-Projekt aus.
    :param project_dir: Pfad zum Gradle-Projektverzeichnis
    """
    if not os.path.isdir(project_dir):
        print(f"Fehler: Das Verzeichnis {project_dir} existiert nicht.")
        return

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
    if projektpfad:
        run_gradle_tests(projektpfad)
    else:
        projektpfad = input("Gib den Pfad zum Gradle-Projekt an: ")
        run_gradle_tests(projektpfad)
