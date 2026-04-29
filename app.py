from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ----------------------------
# DATABASE SETUP
# ----------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foerderungen.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------------
# MODEL
# ----------------------------
class Foerderung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    beschreibung = db.Column(db.String(300))
    voraussetzungen = db.Column(db.Text)
    zielgruppe = db.Column(db.String(100))
    hoehe = db.Column(db.String(100))


# ----------------------------
# INIT DB + SAMPLE DATA
# ----------------------------
@app.before_first_request
def setup():
    db.create_all()

    if Foerderung.query.count() == 0:

        sample = [
            Foerderung(
                name="BAföG",
                beschreibung="Finanzielle Unterstützung für Studierende.",
                voraussetzungen="Studium;unter 45;geringes Einkommen",
                zielgruppe="student",
                hoehe="Bis 934€ monatlich"
            ),
            Foerderung(
                name="Wohngeld",
                beschreibung="Zuschuss zur Miete.",
                voraussetzungen="eigene Wohnung;geringes Einkommen",
                zielgruppe="alle",
                hoehe="abhängig von Einkommen"
            ),
            Foerderung(
                name="Kindergeld",
                beschreibung="Unterstützung für Familien.",
                voraussetzungen="unter 25",
                zielgruppe="familie",
                hoehe="250€ monatlich"
            )
        ]

        db.session.add_all(sample)
        db.session.commit()


# ----------------------------
# HOME PAGE (LISTE AUS DB)
# ----------------------------
@app.route("/")
def home():

    foerderungen = Foerderung.query.all()

    html = """
    <html>
    <head>
        <title>Förderungen DB System</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: 40px auto; }
            .card { border:1px solid #ccc; padding:15px; margin:10px 0; border-radius:8px; }
        </style>
    </head>
    <body>

    <h1>💸 Förderungen Datenbank</h1>
    <p>Alle Förderungen werden aus der Datenbank geladen.</p>
    """

    for f in foerderungen:

        voraus = f.voraussetzungen.split(";")

        html += f"""
        <div class="card">
            <h2>{f.name}</h2>
            <p>{f.beschreibung}</p>
            <p><b>Höhe:</b> {f.hoehe}</p>

            <p><b>Voraussetzungen:</b></p>
            <ul>
        """

        for v in voraus:
            html += f"<li>{v}</li>"

        html += "</ul></div>"

    html += "</body></html>"

    return html


# ----------------------------
# ADD FOERDERUNG (für später Admin)
# ----------------------------
@app.route("/add", methods=["POST"])
def add():

    data = request.json

    f = Foerderung(
        name=data["name"],
        beschreibung=data["beschreibung"],
        voraussetzungen=";".join(data["voraussetzungen"]),
        zielgruppe=data["zielgruppe"],
        hoehe=data["hoehe"]
    )

    db.session.add(f)
    db.session.commit()

    return {"status": "ok"}


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)