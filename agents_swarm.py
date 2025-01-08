import os
import json
from openai import OpenAI

# API-Schlüssel über Umgebungsvariablen einlesen
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("Umgebungsvariable 'API_KEY' ist nicht gesetzt.")

# OpenAI-Client initialisieren
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def log_to_stdout(message_type, content):
    """
    Protokolliert eine Nachricht auf stdout.
    """
    print(f"[{message_type}] {content}")

def send_request_to_llm(prompt):
    """
    Sendet eine Anfrage an das LLM und gibt die Antwort zurück.
    """
    log_to_stdout("REQUEST", prompt)
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        n=1,
        messages=[
            {"role": "system", "content": "Du bist ein hilfreicher Assistent."},
            {"role": "user", "content": prompt}
        ]
    )
    response_content = response.choices[0].message.content
    log_to_stdout("RESPONSE", response_content)
    return response_content

def split_task_into_subtasks(task):
    """
    Fragt das LLM, wie eine Aufgabe in kleinere Aufgaben unterteilt werden kann.
    """
    prompt = (
        f"""
        Teile die folgende Aufgabe in kleinere Aufgaben auf und gib die Antwort im JSON-Format:
        {{
            "subtasks": ["Subtask 1", "Subtask 2", "..."]
        }}
        Aufgabe: {task}
        """
    )
    response = send_request_to_llm(prompt)
    try:
        result = json.loads(response)
        return result.get("subtasks", [])
    except json.JSONDecodeError:
        print("Fehler beim Parsen der LLM-Antwort. Versuche, die Antwort zu reparieren...")
        # Repariere die JSON-Daten, indem Einrückungen entfernt werden
        cleaned_response = "\n".join(line.strip() for line in response.splitlines())
        try:
            result = json.loads(cleaned_response)
            return result.get("subtasks", [])
        except json.JSONDecodeError:
            print("Reparatur fehlgeschlagen. Antwort bleibt unbrauchbar:", response)
            return []

def process_task(task):
    """
    Verarbeitet eine Aufgabe rekursiv. Wenn die Aufgabe nicht weiter unterteilt werden kann,
    wird sie direkt vom LLM bearbeitet.
    """
    subtasks = split_task_into_subtasks(task)

    if not subtasks:  # Wenn keine Subtasks vorhanden sind
        print(f"Bearbeite Aufgabe: {task}")
        prompt = f"Bearbeite die folgende Aufgabe: {task}"
        result = send_request_to_llm(prompt)
        return {"task": task, "result": result}

    results = []
    for subtask in subtasks:
        results.append(process_task(subtask))

    return {"task": task, "subtasks": results}

def aggregate_results(results):
    """
    Fasst die Ergebnisse aller bearbeiteten Aufgaben zusammen.
    """
    if "result" in results:
        return results["result"]

    aggregated = "\n".join(
        aggregate_results(subtask) for subtask in results.get("subtasks", [])
    )
    return aggregated

if __name__ == "__main__":
    # Beispielaufgabe
    initial_task = "Erstelle ein Projektplan für ein KI-gestütztes Chat-System."

    # Verarbeite die Aufgabe rekursiv
    results = process_task(initial_task)

    # Aggregiere die Ergebnisse
    final_result = aggregate_results(results)

    print("\nAbschließendes Ergebnis:")
    print(final_result)
