from flask import Flask, request
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BAföG KI Assistent</title>
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

        <h1>BAföG KI Assistent</h1>

        <p>Erstelle automatisch einen offiziellen Antragstext in Sekunden.</p>

        <form action="/submit" method="post">

            <label>Alter *</label>
            <input name="age" required>

            <label>Studiengang *</label>
            <input name="study" required>

            <label>Semester *</label>
            <input name="semester" required>

            <label>Nebenjob (ja/nein)</label>
            <input name="job">

            <label>Monatliches Einkommen</label>
            <input name="income">

            <label>Wohnsituation</label>
            <input name="living">

            <button type="submit">Antrag generieren</button>
        </form>

        <p class="note">
            Hinweis: Dieses Tool ersetzt keine offizielle Beratung.
        </p>

    </body>
    </html>
    """


# ----------------------------
# FORM HANDLING
# ----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    # Daten sammeln
    answers = {
        "age": request.form.get("age"),
        "study": request.form.get("study"),
        "semester": request.form.get("semester"),
        "job": request.form.get("job") or "nicht angegeben",
        "income": request.form.get("income") or "nicht angegeben",
        "living": request.form.get("living") or "nicht angegeben",
    }

    # Minimal-Validation
    if not answers["age"] or not answers["study"] or not answers["semester"]:
        return "<h2>Bitte alle Pflichtfelder (Alter, Studium, Semester) ausfüllen.</h2>"

    # 🧠 Stabiler Prompt
    prompt = f"""
Du bist ein erfahrener Sachbearbeiter für BAföG-Anträge in Deutschland.

Erstelle aus den folgenden Informationen einen offiziellen, sachlichen Antragstext.

REGELN:
- keine Annahmen oder Erfindungen
- nur vorhandene Daten verwenden
- fehlende Infos neutral erwähnen
- klare, formale Amtssprache
- gut strukturierte Absätze

DATEN:
Alter: {answers["age"]}
Studiengang: {answers["study"]}
Semester: {answers["semester"]}
Nebenjob: {answers["job"]}
Einkommen: {answers["income"]}
Wohnsituation: {answers["living"]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        result = response.choices[0].message.content

    except Exception as e:
        return f"<h2>Fehler bei der KI-Anfrage:</h2><p>{str(e)}</p>"

    # Ergebnisseite
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ergebnis</title>
        <style>
            body {{
                font-family: Arial;
                max-width: 700px;
                margin: 40px auto;
            }}

            pre {{
                background: #f4f4f4;
                padding: 20px;
                white-space: pre-wrap;
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
# START SERVER
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)