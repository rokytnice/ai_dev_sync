# Programm in python - API-Aufruf zur Prompt-Verarbeitung

# Rest Client / request senden
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
## Wartezeit visualisieren:
Zeige während des Wartens auf die API-Antwort eine visuelle Ausgabe auf der Konsole (z. B. Fortschrittsbalken oder animierte Punkte).

# Erweiterung des Prompts durch Dateiinhalte:


# Verzeichniss auslesen / prompt bauen
Schreibe Methoden, die den Prompt erweitern, indem:

Geprüft wird, ob Dateinamen im Prompt enthalten sind.
Die angegebenen Dateien in einem definierten Verzeichnis gesucht werden und
falls eine oder mehr Datei existieren, sollen der Inhalt in den Prompt aufgenommen werden.
Die Verzeichnisse soll rekursiv durchsucht werden.
Wenn ein entsprechendes Verzeichnis adressiert ist mit dem pattern dann wird das Ganze Verzeichnis ausgelesen das bedeutet jede einzelne Datei der Inhalt wird Teil des Proms

base_directory Arbeitsverzeichnis oder Word directory ist immer der übergebene Pfad
Der Arbeitsordner (working directory) und der übergebene Pfad sollen identisch sein.


# logging 
## Logging-Anforderungen:
### Logging des Requests und Responses
Logge den vollständigen Request und die API-Antwort (Response).

## Logging der Dateiverarbeitung:
Logge alle eingelesenen Dateien, die für den Request verwendet werden.
Logge Aktivitäten auf dem Dateisystem, die Änderungen verursachen (z. B. Dateiaktualisierungen oder Neuanlagen).
Logg jede Änderung die du am Dateisystem vorgenommen hast, das schließt auch Änderung von dateienhalten ein



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


Der Response enthält ein json feld text dessen Wert verarbeitet werden muss

Code der aktualisiert werden soll ist entsprechend mit mark-up-code markiert z.B für Java:
"```java"

Stelle sicher dass die Java Klassen die übergeben worden sind und Teil des responses auch im dataeisystem aktualisiert werden
erstelle einen entsprechendes logging in dem klar dargestellt wird was sich geändert hat am Inhalt der Datei
Wenn sich Dateiinhalte geändert habe mache einen diff  und Stelle im Log da was ich geändert hat
Bevor eine Klasse neu angelegt wird soll auf jeden Fall das übergebene Verzeichnis rekursiv durchsucht werden ob diese Klasse vorhanden ist und wenn sie vorhanden ist soll sie ersetzt werden
Die gesendete Java Klasse muss im Dateipfad  aktualisiert werden   java üblich ist
neue Klassen im response müssen dem richtigen Klassennamen gespeichert worden wie es in java üblich ist



Der Name der Klasse sollte auch der Name für die Datei sein so wie in Java üblich
Die package Angabe definiert innerhalb des übergebenen Pfades die Verzeichnisstruktur so wie ja aber üblich


So sieht eine zb ein möglicher response aus:

{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "```java\npackage fwat.application.security;\n\nimport jakarta.servlet.http.HttpServletRequest;\nimport jakarta.servlet.http.HttpServletResponse;\nimport lombok.extern.slf4j.Slf4j;\nimport org.springframework.http.MediaType;\nimport org.springframework.security.core.AuthenticationException;\nimport org.springframework.security.web.authentication.AuthenticationFailureHandler;\n\nimport java.io.IOException;\n\n@Slf4j\npublic class CustomAuthenticationFailureHandler implements AuthenticationFailureHandler {\n\n    @Override\n    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,\n                                        AuthenticationException exception) throws IOException {\n\n        String exceptionMessage = exception.getMessage();\n        String username = request.getParameter(\"username\"); //Attempt to get username\n\n        log.error(\"AUTH-001: Login failed for user '{}'. Exception: {}\", username != null ? username : \"unknown\", exceptionMessage);\n        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);\n        response.setContentType(MediaType.APPLICATION_JSON_VALUE);\n        response.getWriter().write(\"{\\\"message\\\":\\\"Login failed\\\"}\");\n        response.getWriter().flush();\n    }\n}\n```\n\n## support.md\n\nThis document outlines support actions for each log ID generated in `CustomAuthenticationFailureHandler.java`.\n\n| Log ID     | Log Message                                            | Support Action                                                                                                                                                              |\n|-------------|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|\n| AUTH-001   | Login failed for user '{}'. Exception: {}              | 1. **Check username:** Verify if the provided username exists in the LDAP directory.  \u003cbr\u003e 2. **Investigate exception:** Analyze the exception message (`{}`) for clues. Common causes include incorrect password, account lockout, or network issues. \u003cbr\u003e 3. **Check LDAP connectivity:** Ensure the application can connect to the LDAP server. \u003cbr\u003e 4. **Review logs:** Examine the application and LDAP server logs for further details. \u003cbr\u003e 5. **Test credentials:** If possible, try logging in with the provided username and password directly into the LDAP directory. \u003cbr\u003e 6. **Account status:** Check the user account status in the LDAP directory (e.g., is it enabled, locked out?). |\n\n\n**General Troubleshooting Steps:**\n\n* **Check application logs:** Review the application logs for more detailed information about the login failure. The log message includes a timestamp and other useful context.\n* **Check LDAP server logs:** Examine the LDAP server logs for any errors or warnings related to authentication attempts.\n* **Network connectivity:** Verify that the application can successfully connect to the LDAP server.  Check network configuration, firewall rules, and DNS resolution.\n* **LDAP configuration:** Review the LDAP configuration in `application.yml` to ensure it is correct.\n* **User account status:** Confirm that the user account is not locked out or disabled in the LDAP directory.\n* **Password reset:**  If the user has forgotten their password, provide instructions for resetting it through the appropriate channels (e.g., a password reset link).\n\n**Note:**  Adding more specific error codes and log messages will greatly enhance troubleshooting capabilities. For example, differentiating between \"Incorrect Password\" and \"Account Locked\" errors would streamline the support process.  The current implementation attempts to extract the username from the request, but this might not always be reliable. A more robust solution would be to include the username in the log message at the point of authentication attempt.\n"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "citationMetadata": {
        "citationSources": [
          {
            "startIndex": 44,
            "endIndex": 195,
            "uri": "https://ttl-blog.tistory.com/category/%F0%9F%8F%9D%EF%B8%8F%20Spring?page=10"
          },
          {
            "startIndex": 218,
            "endIndex": 382,
            "uri": "https://auth0.com/blog/get-started-with-custom-error-handling-in-spring-boot-java/"
          },
          {
            "startIndex": 370,
            "endIndex": 520,
            "uri": "https://github.com/PCloud63514/SpringBootSecuritySample"
          },
          {
            "startIndex": 502,
            "endIndex": 690,
            "uri": "https://auth0.com/blog/get-started-with-custom-error-handling-in-spring-boot-java/"
          },
          {
            "startIndex": 551,
            "endIndex": 725,
            "uri": "https://github.com/ecvheo1/spring-security-jwt"
          },
          {
            "startIndex": 1011,
            "endIndex": 1157,
            "uri": "https://github.com/abhijithms123/AssetManagerSpringboot"
          }
        ]
      },
      "avgLogprobs": -0.27732757811850689
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 12633,
    "candidatesTokenCount": 752,
    "totalTokenCount": 13385
  },
  "modelVersion": "gemini-1.5-flash"
}

Achte darauf dass nur der Teil des Java Markups in der Datei landet



# Hinweise
Der Code sollte modular aufgebaut sein, um die Anforderungen an Logging, Dateiverarbeitung und API-Integration sauber zu trennen.
Achte auf eine klare Fehlerbehandlung für fehlende Dateien, ungültige Pfade und API-Fehler.
Tests sollten nicht nur funktional sein, sondern auch Randfälle abdecken (z. B. keine Dateien vorhanden, ungültiger API-Key, etc.).
Stelle sicher, dass:
Der Prompt korrekt verarbeitet wird.
Dateien im definierten Pfad ordnungsgemäß gesucht, gelesen und in den Request integriert werden.
Der Response korrekt interpretiert wird und alle notwendigen Änderungen an den Dateien vorgenommen werden.
Lagere den Teil des Hauptprogramms aus in eine extra Datei

Die zu aktualisierenden Datei aus dem response muss im übergebenen Verzeichnis gesucht werden und aktualisiert werden


# start & test
Parameter für einen Staat sind z.B eine Liste von Faden und ein Text(propt)
hier 2 beispiele:



## tests


### testfall update java klasse
pfade: /home/andre/IdeaProjects/algosec-connector
prompt: "Aktualisiere CustomAuthenticationFailureHandler.java Java-Klasse Füge eine errorcode zu dem log staement hinzu."







### Testfall betriebshandbuch erstellen:
Prompt: Erstelle eine betriebshandbuch

pfade: /home/andre/IdeaProjects/algosec-connector/src/**.java,
/home/andre/IdeaProjects/algosec-connector/*



        

## Probleme beheben
ein e find_existing_or_new_path nicht korrekt referenziert wird. Sie befindet sich in der Klasse ResponseHandler, greift aber auf self.file_manager zu, wo die Methode nicht existiert. Ich werde das Problem beheben, indem die Methode korrekt in die Klasse FileManager verschoben wird und dort aufgerufen wird. Hier ist die aktualisierte Version:

Bearbeitet
Der Fehler wurde behoben, indem die Methode find_existing_or_new_path in die Klasse FileManager verschoben wurde. Die Klasse ResponseHandler verwendet nun korrekt self.file_manager.find_existing_or_new_path, um bestehende Dateien zu überprüfen oder neue Pfade zu erstellen. Testen Sie die Änderungen, und geben Sie mir Bescheid, ob alles wie erwartet funktioniert!
