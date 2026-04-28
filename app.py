from flask import Flask, request
import os

app = Flask(__name__)


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BAföG Assistent</title>
        <style>
            body {
                font-family: Arial;
                max-width: 650px;
                margin: 50px auto;
                padding: 20px;
            }

            input {
                width: 100%;
                padding: 10px;
                margin: 6px 0;
            }

            button {
                width: 100%;
                padding: 12px;
                background: black;
                color: white;
                border: none;
                cursor: pointer;
                margin-top: 10px;
            }

            button:hover {
                background: #333;
            }

            .note {
                font-size: 12px;
                color: gray;
                margin-top: 20px;
            }
        </style>
    </head>

    <body>

        <h1>BAföG Assistent</h1>

        <p>Erstelle einen professionellen Antragstext für dein BAföG.</p>

        <form action="/submit" method="post">

            <input name="age" placeholder="Alter *" required>
            <input name="study" placeholder="Studiengang *" required>
            <input name="semester" placeholder="Semester *" required>

            <input name="job" placeholder="Nebenjob (ja/nein)">
            <input name="income" placeholder="Monatliches Einkommen">
            <input name="living" placeholder="Wohnsituation (bei Eltern / allein / WG)">

            <button type="submit">Antrag erstellen</button>
        </form>

        <p class="note">
            Hinweis: Dieses Tool ersetzt keine offizielle BAföG-Beratung.
        </p>

    </body>
    </html>
    """


# ----------------------------
# FORM HANDLING (PROFESSIONELL OHNE KI)
# ----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    data = {
        "age": request.form.get("age"),
        "study": request.form.get("study"),
        "semester": request.form.get("semester"),
        "job": request.form.get("job") or "nicht angegeben",
        "income": request.form.get("income") or "nicht angegeben",
        "living": request.form.get("living") or "nicht angegeben",
    }

    # Pflichtfelder prüfen
    if not data["age"] or not data["study"] or not data["semester"]:
        return "<h2>Bitte füllen Sie alle Pflichtfelder (Alter, Studium, Semester) aus.</h2>"

    # ----------------------------
    # INTELLIGENTE TEXTLOGIK (OHNE KI)
    # ----------------------------

    income_text = (
        f"Der Antragsteller erzielt ein monatliches Einkommen von {data['income']} Euro."
        if data["income"] != "nicht angegeben"
        else "Es wurde kein Einkommen angegeben."
    )

    job_text = (
        "Es wird ein Nebenjob ausgeübt."
        if data["job"].lower() == "ja"
        else "Es wird kein Nebenjob ausgeübt."
    )

    living_text = f"Die Wohnsituation lautet: {data['living']}."

    # Professioneller Antragstext
    result = f"""
BAföG-ANTRAG – AUTOMATISCH ERSTELLTE ZUSAMMENFASSUNG

1. Persönliche Angaben
Der Antragsteller ist {data["age"]} Jahre alt und studiert {data["study"]} im {data["semester"]}. Semester.

2. Studium
Derzeit wird ein Studium im Bereich {data["study"]} absolviert.

3. Finanzielle Situation
{job_text}
{income_text}

4. Wohnsituation
{living_text}

5. Erklärung
Diese Zusammenfassung wurde automatisch erstellt und dient als strukturierte Übersicht für den BAföG-Antrag.

Alle Angaben sind vor Abgabe eigenständig zu prüfen und gegebenenfalls zu korrigieren.
"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ergebnis</title>
        <style>
            body {{
                font-family: Arial;
                max-width: 750px;
                margin: 40px auto;
            }}

            pre {{
                background: #f4f4f4;
                padding: 20px;
                white-space: pre-wrap;
                line-height: 1.5;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
            }}
        </style>
    </head>

    <body>

        <h1>Dein BAföG Antrag</h1>

        <pre>{result}</pre>

        <a href="/">← Zurück</a>

    </body>
    </html>
    """


# ----------------------------
# START (RENDER READY)
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)