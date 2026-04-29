from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ----------------------------
# DATABASE CONFIG
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
# INIT DATABASE SAFELY
# ----------------------------
def init_db():
    with app.app_context():
        db.create_all()

        # Demo-Daten nur wenn leer
        if Foerderung.query.count() == 0:
            demo = Foerderung(
                name="BAföG",
                beschreibung="Finanzielle Unterstützung für Studierende.",
                voraussetzungen="Studium;unter 45;geringes Einkommen",
                zielgruppe="student",
                hoehe="bis zu 934€ monatlich"
            )
            db.session.add(demo)
            db.session.commit()


init_db()


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    items = Foerderung.query.all()

    html = """
    <html>
    <head>
        <title>Förderungen Übersicht</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: 40px auto; }
            .card { border:1px solid #ddd; padding:15px; margin:10px 0; border-radius:8px; }
            a.button {
                display:inline-block;
                padding:10px 15px;
                background:black;
                color:white;
                text-decoration:none;
                margin-bottom:20px;
                border-radius:5px;
            }
        </style>
    </head>
    <body>

    <h1>💸 Förderungen Übersicht</h1>

    <a class="button" href="/admin">➕ Neue Förderung hinzufügen</a>
    """

    for f in items:
        html += f"""
        <div class="card">
            <h2>{f.name}</h2>
            <p>{f.beschreibung}</p>
            <p><b>Höhe:</b> {f.hoehe}</p>
            <p><b>Zielgruppe:</b> {f.zielgruppe}</p>

            <p><b>Voraussetzungen:</b></p>
            <ul>
        """

        for v in f.voraussetzungen.split(";"):
            html += f"<li>{v}</li>"

        html += "</ul></div>"

    html += "</body></html>"

    return html


# ----------------------------
# ADMIN PAGE
# ----------------------------
@app.route("/admin")
def admin():
    return """
    <html>
    <head>
        <title>Admin Panel</title>
        <style>
            body { font-family: Arial; max-width:600px; margin:40px auto; }
            input { width:100%; padding:10px; margin:6px 0; }
            button { width:100%; padding:12px; background:black; color:white; border:none; }
        </style>
    </head>

    <body>

        <h1>➕ Förderung hinzufügen</h1>

        <form action="/add" method="post">

            <input name="name" placeholder="Name" required>
            <input name="beschreibung" placeholder="Beschreibung" required>
            <input name="voraussetzungen" placeholder="Voraussetzungen (; getrennt)" required>
            <input name="zielgruppe" placeholder="Zielgruppe (student, azubi, familie)" required>
            <input name="hoehe" placeholder="Höhe" required>

            <button type="submit">Speichern</button>

        </form>

        <br>
        <a href="/">← Zurück</a>

    </body>
    </html>
    """


# ----------------------------
# ADD ROUTE
# ----------------------------
@app.route("/add", methods=["POST"])
def add():

    new_f = Foerderung(
        name=request.form.get("name"),
        beschreibung=request.form.get("beschreibung"),
        voraussetzungen=request.form.get("voraussetzungen"),
        zielgruppe=request.form.get("zielgruppe"),
        hoehe=request.form.get("hoehe")
    )

    db.session.add(new_f)
    db.session.commit()

    return redirect("/")


# ----------------------------
# START (RENDER READY)
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)