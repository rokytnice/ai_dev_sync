Erstelle mir ein Programm das einen prompt an eine api schickt
Wieder auch wie fest auszusehen hat zeigt der folgende curl befehl


curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
  "contents": [{
    "parts":[{"text": "Explain how AI works"}]
    }]
   }'

Der prompt der über den rückwärts verschickt wird wird wie folgt gebildet:

Erstelle mir Methoden zum Erweitern des prompt
In den Methoden soll geschaut werden ob der Name einer Datei auftaucht
Wenn der Name einer Datei auftaucht dann soll in einem übergebenen Pfad geschaut werden ob die Datei vorhanden ist und wenn ja soll der Inhalt zu dem prompt hinzugefügt werden
Das Verzeichnis ist rekursiv zu durchsuchen


Der Response enthält einen Body mit der Antwort
Sollte dieser dieser Body einen Dateinamen oder mehrere enthalten dann soll in dem Pfad gesucht werden nach den Dateien und diese dann aktualisiert werden
sind  die Dateien nicht enthalten sollte sie neu angelegt werden


Baue ein entsprechendes logging dass mir den Request und den response ausgibt

logge Auch die Aktivitäten auf dem Dateisystem zu Änderung führen



Der API key soll von der Umgebungsvariable gelesen werden
 

Wenn ein Pfad angegeben worden ist dann und kein expliziter Dateiname dann ist der Inhalt aller Dateien einzulesen und der prompt entsprechend zu erweitern dabei ist darauf zu achten dass rekursiv alle Unterverzeichnisse berücksichtigt werden




Erstelle entsprechende Tests

Erstelle einen Test mit folgenden Dateipfad /home/andre/IdeaProjects/algosec-connector/src
Der Inhalt des promtes soll sein:
Mach mir eine Analyse auf Basis des BSI grundschutzes


Working directory und der Pfad sind das gleiche
 

Der response hat ein Feld Text dieser Inhalt soll formatiert ausgegeben werden dabei sollen entsprechende Zeichen für die Zeilenumbrüche richtig interpretiert werden