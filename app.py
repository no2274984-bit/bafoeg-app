from flask import Flask
import os

app = Flask(__name__)

# ----------------------------
# DATENBANK (EINFACH ALS LISTE)
# ----------------------------
foerderungen = [
    {
        "name": "BAföG",
        "beschreibung": "Finanzielle Unterstützung für Studierende.",
        "voraussetzungen": [
            "Im Studium oder schulischer Ausbildung",
            "Unter 45 Jahre",
            "Geringes Einkommen",
            "Deutsche Staatsbürgerschaft oder Aufenthaltstitel"
        ],
        "hoehe": "Bis zu ca. 934€ monatlich"
    },
    {
        "name": "Wohngeld",
        "beschreibung": "Zuschuss zur Miete.",
        "voraussetzungen": [
            "Eigene Wohnung",
            "Geringes Einkommen",
            "Kein BAföG-Bezug"
        ],
        "hoehe": "Abhängig von Miete und Einkommen"
    },
    {
        "name": "Kindergeld",
        "beschreibung": "Monatliche Zahlung für Kinder.",
        "voraussetzungen": [
            "Unter 25 Jahre (bei Ausbildung/Studium)",
            "Eltern erhalten Zahlung"
        ],
        "hoehe": "250€ pro Monat"
    },
    {
        "name": "Bürgergeld",
        "beschreibung": "Grundsicherung für Arbeitssuchende.",
        "voraussetzungen": [
            "Erwerbsfähig",
            "Geringes oder kein Einkommen",
            "Wohnsitz in Deutschland"
        ],
        "hoehe": "Regelsatz + Unterkunftskosten"
    }
]


# ----------------------------
# HOME (ÜBERSICHT)
# ----------------------------
@app.route("/")
def home():

    html = """
    <html>
    <head>
        <title>Förderungen Überblick</title>
        <style>
            body {
                font-family: Arial;
                max-width: 800px;
                margin: 40px auto;
            }

            .card {
                border: 1px solid #ccc;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
            }

            h2 {
                margin-bottom: 5px;
            }

            ul {
                margin-top: 10px;
            }
        </style>
    </head>

    <body>

        <h1>💸 Staatliche Förderungen in Deutschland</h1>
        <p>Hier findest du eine Übersicht über wichtige Zuschüsse und deren Voraussetzungen.</p>
    """

    for f in foerderungen:
        html += f"""
        <div class="card">
            <h2>{f['name']}</h2>
            <p><b>Beschreibung:</b> {f['beschreibung']}</p>
            <p><b>Höhe:</b> {f['hoehe']}</p>

            <p><b>Voraussetzungen:</b></p>
            <ul>
        """

        for v in f["voraussetzungen"]:
            html += f"<li>{v}</li>"

        html += "</ul></div>"

    html += """
    </body>
    </html>
    """

    return html


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)