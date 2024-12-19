# Programm in python - API-Aufruf zur Prompt-Verarbeitung

# Rest Client
Implementiere ein Programm, das einen Prompt an die folgende API sendet:
vbnet
Code kopieren
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
  "contents": [{
    "parts":[{"text": "Explain how AI works"}]
  }]
}'
# env
Der API-Key soll nicht hardcodiert sein, sondern aus einer Umgebungsvariable gelesen werden.


# Erweiterung des Prompts durch Dateiinhalte:


# Verzeichniss auslesen / prompt bauen
Schreibe Methoden, die den Prompt erweitern, indem:

Geprüft wird, ob Dateinamen im Prompt enthalten sind.
Die angegebenen Dateien in einem definierten Verzeichnis gesucht werden.
Falls eine oder mehr Datei existieren, sollen der Inhalt in den Prompt aufgenommen werden.
Die Verzeichnis soll rekursiv durchsucht werden.

Der Arbeitsordner (working directory) und der übergebene Pfad sollen identisch sein.


# logging
Logging-Anforderungen
Logging des Requests und Responses:

Logge den vollständigen Request und die API-Antwort (Response).
Logging der Dateiverarbeitung:

Logge alle eingelesenen Dateien, die für den Request verwendet werden.
Logge Aktivitäten auf dem Dateisystem, die Änderungen verursachen (z. B. Dateiaktualisierungen oder Neuanlagen).



# Verarbeitung von Verzeichnissen:

Es können beliebig viele Pfade zu Verzeichnissen oder zu Dateien übergeben werden
Werden Verzeichnisse übergeben sind alle Dateien und die Unterverzeichnisse mit Dateien relevant
Wird ein Pfad zu einer Datei übergeben ist diese relevant
Berücksichtige rekursiv immer alle Unterverzeichnisse.

##  Glob-Mustern
 Glob-Mustern wird verwendet um Dateien und Verzeichnisse zu beschreiben
Es können Wildcards verwendet werden um bestimmte Dateitypen oder bestimmte namens Muster zu definieren so wie es allgemein üblich ist


# Verarbeitung des Responses

Der Response enthält einen Body mit einem oder mehreren Dateinamen.
Suche diese Dateien im definierten Pfad.
Falls vorhanden: Aktualisiere die Inhalte der Dateien basierend auf der Antwort.
Falls nicht vorhanden: Lege neue Dateien mit den entsprechenden Inhalten an.

Das Feld text im Response soll formatiert ausgegeben werden.
Interpretiere dabei Zeichen wie Zeilenumbrüche korrekt.
Wartezeit visualisieren:

Zeige während des Wartens auf die API-Antwort eine visuelle Ausgabe auf der Konsole (z. B. Fortschrittsbalken oder animierte Punkte).


# Testanforderungen
Testfall erstellen:
Erstelle einen Test, bei dem der Prompt lautet:

Erstelle eine betriebshandbuch
/home/andre/IdeaProjects/algosec-connector/src/**.java,
/home/andre/IdeaProjects/algosec-connector/*
Stelle sicher, dass:
Der Prompt korrekt verarbeitet wird.
Dateien im definierten Pfad ordnungsgemäß gesucht, gelesen und in den Request integriert werden.
Der Response korrekt interpretiert wird und alle notwendigen Änderungen an den Dateien vorgenommen werden.

# Hinweise

Der Code sollte modular aufgebaut sein, um die Anforderungen an Logging, Dateiverarbeitung und API-Integration sauber zu trennen.
Achte auf eine klare Fehlerbehandlung für fehlende Dateien, ungültige Pfade und API-Fehler.
Tests sollten nicht nur funktional sein, sondern auch Randfälle abdecken (z. B. keine Dateien vorhanden, ungültiger API-Key, etc.).