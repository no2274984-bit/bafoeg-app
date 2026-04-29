from flask import Flask, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ----------------------------
# SECURITY
# ----------------------------
app.secret_key = "change-this-secret-key-immediately"

# ----------------------------
# DATABASE (Render safe)
# ----------------------------
DB_PATH = os.environ.get("DB_PATH", "foerderungen.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------------
# ADMIN ACCOUNT
# ----------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


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
# INIT DB SAFELY
# ----------------------------
with app.app_context():
    db.create_all()

    if Foerderung.query.count() == 0:
        db.session.add(Foerderung(
            name="BAföG",
            beschreibung="Studienförderung für Studierende",
            voraussetzungen="Studium;Einkommen niedrig",
            zielgruppe="student",
            hoehe="bis 934€ monatlich"
        ))
        db.session.commit()


# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/")
        else:
            return "<h3>Falscher Login</h3>"

    return """
    <h2>Admin Login</h2>
    <form method="post">
        <input name="username" placeholder="Username" required><br><br>
        <input name="password" type="password" placeholder="Passwort" required><br><br>
        <button type="submit">Login</button>
    </form>
    """


# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


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
            .box { border:1px solid black; padding:15px; margin-top:20px; }
            input { width:100%; padding:10px; margin:5px 0; }
            button { padding:10px; background:black; color:white; border:none; }
        </style>
    </head>
    <body>

    <h1>💸 Förderungen Übersicht</h1>
    """

    # LOGIN STATUS
    if session.get("admin"):
        html += "<p>🔐 Admin eingeloggt | <a href='/logout'>Logout</a></p>"
    else:
        html += "<a href='/login'>Admin Login</a>"

    # LISTE
    for f in items:
        html += f"""
        <div class="card">
            <h2>{f.name}</h2>
            <p>{f.beschreibung}</p>
            <p><b>Höhe:</b> {f.hoehe}</p>

            <b>Voraussetzungen:</b>
            <ul>
        """

        for v in f.voraussetzungen.split(";"):
            html += f"<li>{v}</li>"

        html += "</ul>"

        if session.get("admin"):
            html += f"""
            <form method="post" action="/delete/{f.id}">
                <button style="background:red;">Löschen</button>
            </form>
            """

        html += "</div>"

    # ADD FORM (ADMIN ONLY)
    if session.get("admin"):
        html += """
        <div class="box">
            <h2>➕ Förderung hinzufügen</h2>

            <form method="post" action="/add">

                <input name="name" placeholder="Name" required>
                <input name="beschreibung" placeholder="Beschreibung" required>
                <input name="voraussetzungen" placeholder="Voraussetzungen (; getrennt)" required>
                <input name="zielgruppe" placeholder="Zielgruppe" required>
                <input name="hoehe" placeholder="Höhe" required>

                <button type="submit">Speichern</button>
            </form>
        </div>
        """

    html += "</body></html>"
    return html


# ----------------------------
# ADD
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
# DELETE
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