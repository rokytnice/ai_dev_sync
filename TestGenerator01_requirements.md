 

**Anforderungen für das Python-Programm zur Ausführung von Java-Tests mit Gradle**

Erstelle ein Python-Programm, das in der Lage ist, Java-Tests mit Gradle auszuführen. Das Programm soll die folgenden Anforderungen erfüllen:

1. **Gradle-Wrapper**: Der `gradlew`-Wrapper befindet sich immer im Verzeichnis des übergebenen Pfades.
2. **Logging**: Jedes ausgeführte Kommando und dessen Ergebnis soll protokolliert werden.
3. **Umgebungsvariable**: Das Projektverzeichnis wird über eine Umgebungsvariable eingelesen. Wenn der Pfad in der Umgebungsvariable enthalten ist, soll nicht nach dem Pfad gefragt werden.
4. **AI-Agent**: Das Programm soll einen AI-Agenten enthalten, der den Quellcode einer Java-Klasse über eine REST-Schnittstelle an ein Sprachmodell (LLM) sendet.
5. **API-Aufruf**: Der Aufruf der Schnittstelle soll wie folgt funktionieren:
   ```sh
   curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=GEMINI_API_KEY" \
   -H 'Content-Type: application/json' \
   -X POST \
   -d '{
     "contents": [{
       "parts":[{"text": "Generiere Testcode für die folgende Java-Klasse: ..."}]
     }]
   }'
   ```
6. **Testklasse generieren**: Der Agent übergibt den Quellcode und die Aufforderung, Testcode zu generieren. Die Antwort enthält eine Java-Testklasse.
7. **Testklasse speichern**: Die Testklasse soll extrahiert und unter `src/test` gespeichert werden.
8. **Testklasse ausführen**: Das Programm soll die Testklasse ausführen und das Ergebnis analysieren.
9. **API-Key**: Der API-Key wird über die Umgebungsvariable `API_KEY` bereitgestellt.

**Zusätzliche Anforderungen:**

- **Eingabeaufforderung**: Beim Start des Programms soll eine Eingabeaufforderung erstellt werden, die den Namen einer Java-Klasse entgegennimmt. Wenn dieser Parameter übergeben wird, soll nur diese Datei verarbeitet werden.
- **Rekursive Suche**: Das Programm soll rekursiv im Verzeichnis `src/main` nach der angegebenen Klasse suchen und diese einlesen.
- **Logging**: Jeder Verarbeitungsschritt (Einlesen, Schreiben und Ausführen einer Datei) soll protokolliert werden. Es soll auch protokolliert werden, in welchen Verzeichnissen gesucht wird.
- **Timeout und Fehlerbehandlung**: Ein Timeout für die API-Anfrage soll auf 30 Sekunden gesetzt werden. Falls die API nicht antwortet oder ein Netzwerkproblem auftritt, soll eine Fehlermeldung protokolliert werden, damit das Programm nicht endlos hängen bleibt.
- **Ordnerstruktur**: Die Ordnerstruktur soll entsprechend dem Paketnamen der erzeugten Testklasse erstellt werden, damit die Dateien im richtigen Pfad abgelegt werden.

**Beispiel für die Erstellung der Ordnerstruktur:**
```python
import os

# Beispiel: Erstelle die Ordnerstruktur für eine Testklasse
package_name = "com.example.myapp"
class_name = "MyTest"

# Erstelle die Verzeichnisse
package_path = os.path.join(project_directory, "src", "test", "java", *package_name.split('.'))
os.makedirs(package_path, exist_ok=True)

# Erstelle die Testklasse
test_class_path = os.path.join(package_path, f"{class_name}.java")
with open(test_class_path, 'w') as file:
    file.write(f"package {package_name};\n\npublic class {class_name} {{\n    // Testmethoden hier\n}}\n")

logging.info(f"Testklasse {class_name} erstellt in {test_class_path}")
```
 