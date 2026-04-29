from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ----------------------------
# CONFIG
# ----------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///foerderungen.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------------
# MODEL
# ----------------------------
class Foerderung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    beschreibung = db.Column(db.String(300), nullable=False)
    voraussetzungen = db.Column(db.Text, nullable=False)
    zielgruppe = db.Column(db.String(100), nullable=False)
    hoehe = db.Column(db.String(100), nullable=False)


# ----------------------------
# SAFE DB INIT (Render-friendly)
# ----------------------------
def init_db():
    with app.app_context():
        db.create_all()

        # nur Demo-Daten wenn leer
        if Foerderung.query.count() == 0:
            db.session.add(Foerderung(
                name="BAföG",
                beschreibung="Finanzielle Unterstützung für Studierende.",
                voraussetzungen="Studium;unter 45;geringes Einkommen",
                zielgruppe="student",
                hoehe="bis zu 934€ monatlich"
            ))
            db.session.commit()


init_db()


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    items = Foerderung.query.all()

    html = """
    <html>
    <head>
        <title>Förderungen Plattform</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: 40px auto; }
            .card { border:1px solid #ddd; padding:15px; margin:10px 0; border-radius:8px; }
            .box { border:1px solid black; padding:15px; margin-top:30px; }
            input { width:100%; padding:10px; margin:5px 0; }
            button { width:100%; padding:12px; background:black; color:white; border:none; }
        </style>
    </head>
    <body>

    <h1>💸 Förderungen Übersicht</h1>
    """

    for f in items:
        html += f"""
        <div class="card">
            <h2>{f.name}</h2>
            <p>{f.beschreibung}</p>
            <p><b>Höhe:</b> {f.hoehe}</p>
            <p><b>Zielgruppe:</b> {f.zielgruppe}</p>

            <b>Voraussetzungen:</b>
            <ul>
        """

        for v in f.voraussetzungen.split(";"):
            html += f"<li>{v}</li>"

        html += "</ul></div>"

    # ----------------------------
    # ADD FORM (kein /admin nötig)
    # ----------------------------
    html += """
    <div class="box">
        <h2>➕ Förderung hinzufügen</h2>

        <form method="post" action="/add">

            <input name="name" placeholder="Name" required>
            <input name="beschreibung" placeholder="Beschreibung" required>
            <input name="voraussetzungen" placeholder="Voraussetzungen (; getrennt)" required>
            <input name="zielgruppe" placeholder="Zielgruppe (student, azubi, familie)" required>
            <input name="hoehe" placeholder="Höhe" required>

            <button type="submit">Speichern</button>

        </form>
    </div>

    </body>
    </html>
    """

    return html


# ----------------------------
# ADD ROUTE
# ----------------------------
@app.route("/add", methods=["POST"])
def add():
    try:
        new_f = Foerderung(
            name=request.form.get("name"),
            beschreibung=request.form.get("beschreibung"),
            voraussetzungen=request.form.get("voraussetzungen"),
            zielgruppe=request.form.get("zielgruppe"),
            hoehe=request.form.get("hoehe")
        )

        db.session.add(new_f)
        db.session.commit()

    except Exception as e:
        return f"Fehler: {str(e)}"

    return redirect("/")


# ----------------------------
# START (IMPORTANT FOR RENDER)
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)