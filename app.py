from flask import Flask, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "secret-key-change-later"

# ----------------------------
# DATABASE (Render safe with disk support)
# ----------------------------
DB_PATH = os.environ.get("DB_PATH", "foerderungen.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------------
# MODEL
# ----------------------------
class Foerderung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    beschreibung = db.Column(db.String(300))
    voraussetzungen = db.Column(db.Text)
    zielgruppe = db.Column(db.String(100))
    hoehe = db.Column(db.String(100))


# ----------------------------
# INIT DB
# ----------------------------
with app.app_context():
    db.create_all()

    if Foerderung.query.count() == 0:
        db.session.add(Foerderung(
            name="BAföG",
            beschreibung="Studienförderung",
            voraussetzungen="Studium;Einkommen niedrig",
            zielgruppe="student",
            hoehe="bis 934€"
        ))
        db.session.commit()


# ----------------------------
# HOME + SEARCH + SECRET ADMIN LOGIN
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def home():

    # 🔐 SECRET LOGIN VIA SEARCH
    if request.method == "POST":
        search = request.form.get("search")

        if search == "27082007":
            session["admin"] = True
            return redirect("/")

    query = Foerderung.query.all()

    html = """
    <html>
    <head>
        <title>Förderungen System</title>
        <style>
            body { font-family: Arial; max-width: 900px; margin: 40px auto; }
            .card { border:1px solid #ddd; padding:15px; margin:10px 0; border-radius:8px; }
            .box { border:1px solid black; padding:15px; margin-top:20px; }
            input { width:100%; padding:10px; margin:5px 0; }
            button { width:100%; padding:12px; background:black; color:white; border:none; }
        </style>
    </head>
    <body>

    <h1>💸 Förderungen</h1>

    <form method="post">
        <input name="search" placeholder="Suche... (oder Enter für Admin-Code)">
        <button type="submit">Suchen</button>
    </form>
    """

    # ----------------------------
    # LISTE
    # ----------------------------
    for f in query:
        html += f"""
        <div class="card">
            <h2>{f.name}</h2>
            <p>{f.beschreibung}</p>
            <p><b>Höhe:</b> {f.hoehe}</p>
        """

        # ADMIN DELETE BUTTON
        if session.get("admin"):
            html += f"""
            <form method="post" action="/delete/{f.id}">
                <button type="submit" style="background:red;">Löschen</button>
            </form>
            """

        html += "</div>"

    # ----------------------------
    # ADMIN PANEL
    # ----------------------------
    if session.get("admin"):
        html += """
        <div class="box">
            <h2>🔐 Admin Mode</h2>

            <form method="post" action="/add">

                <input name="name" placeholder="Name" required>
                <input name="beschreibung" placeholder="Beschreibung" required>
                <input name="voraussetzungen" placeholder="Voraussetzungen (; getrennt)" required>
                <input name="zielgruppe" placeholder="Zielgruppe" required>
                <input name="hoehe" placeholder="Höhe" required>

                <button type="submit">Hinzufügen</button>
            </form>
        </div>
        """

    html += "</body></html>"
    return html


# ----------------------------
# ADD FOERDERUNG
# ----------------------------
@app.route("/add", methods=["POST"])
def add():
    if not session.get("admin"):
        return "Nicht erlaubt"

    f = Foerderung(
        name=request.form.get("name"),
        beschreibung=request.form.get("beschreibung"),
        voraussetzungen=request.form.get("voraussetzungen"),
        zielgruppe=request.form.get("zielgruppe"),
        hoehe=request.form.get("hoehe")
    )

    db.session.add(f)
    db.session.commit()

    return redirect("/")


# ----------------------------
# DELETE FOERDERUNG
# ----------------------------
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    if not session.get("admin"):
        return "Nicht erlaubt"

    f = Foerderung.query.get(id)
    if f:
        db.session.delete(f)
        db.session.commit()

    return redirect("/")


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)