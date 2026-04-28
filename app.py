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
# FORM HANDLING
# ----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    try:
        data = {
            "age": request.form.get("age"),
            "study": request.form.get("study"),
            "semester": request.form.get("semester"),
            "job": request.form.get("job") or "nicht angegeben",
            "income": request.form.get("income") or "nicht angegeben",
            "living": request.form.get("living") or "nicht angegeben",
        }

        # Pflichtfelder check
        if not data["age"] or not data["study"] or not data["semester"]:
            return "<h2>Bitte Pflichtfelder ausfüllen</h2>"

        prompt = f"""
Du bist ein erfahrener Sachbearbeiter für BAföG-Anträge in Deutschland.

Erstelle einen offiziellen, sachlichen Antragstext.

Regeln:
- nur echte Daten verwenden
- nichts erfinden
- fehlende Infos neutral erwähnen
- klare Amtssprache
- strukturierte Absätze

Daten:
Alter: {data["age"]}
Studiengang: {data["study"]}
Semester: {data["semester"]}
Nebenjob: {data["job"]}
Einkommen: {data["income"]}
Wohnsituation: {data["living"]}
"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        result = response.choices[0].message.content

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

    except Exception as e:
        return f"<h2>Fehler:</h2><p>{str(e)}</p>"


# ----------------------------
# START (WICHTIG FÜR RENDER)
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)