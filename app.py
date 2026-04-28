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

        <h1>BAföG Assistent</h1>

        <p>Erstelle automatisch einen Antragstext in Sekunden.</p>

        <form action="/submit" method="post">

            <input name="age" placeholder="Alter *" required>
            <input name="study" placeholder="Studiengang *" required>
            <input name="semester" placeholder="Semester *" required>

            <input name="job" placeholder="Nebenjob (ja/nein)">
            <input name="income" placeholder="Monatliches Einkommen">
            <input name="living" placeholder="Wohnsituation">

            <button type="submit">Antrag generieren</button>
        </form>

        <p class="note">
            Hinweis: Dieses Tool ersetzt keine offizielle Beratung.
        </p>

    </body>
    </html>
    """


# ----------------------------
# FORM HANDLING (OHNE KI)
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

    # Pflichtcheck
    if not data["age"] or not data["study"] or not data["semester"]:
        return "<h2>Bitte Pflichtfelder ausfüllen (Alter, Studium, Semester)</h2>"

    # 🧠 Automatisch generierter Antrag (ohne KI)
    result = f"""
BAföG-Antrag (automatisch erstellt)

Persönliche Angaben:
- Alter: {data["age"]}
- Studiengang: {data["study"]}
- Semester: {data["semester"]}

Finanzielle Situation:
- Nebenjob: {data["job"]}
- Monatliches Einkommen: {data["income"]}

Wohnsituation:
- {data["living"]}

Hinweis:
Dieser Antrag wurde automatisch erstellt und dient nur als Orientierung.
Bitte prüfen Sie alle Angaben vor der Abgabe.
"""

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
# START SERVER (RENDER READY)
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)