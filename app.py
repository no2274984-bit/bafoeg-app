from flask import Flask, request, redirect, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

database_url = os.environ.get("DATABASE_URL", "sqlite:///foerderungen.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----------------------------
# MODELS
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    typ = db.Column(db.String(50))
    einkommen = db.Column(db.Integer)


class Foerderung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    beschreibung = db.Column(db.String(300))
    zielgruppe = db.Column(db.String(100))
    min_einkommen = db.Column(db.Integer)
    max_einkommen = db.Column(db.Integer)
    hoehe = db.Column(db.String(100))


class Antrag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    foerderung_id = db.Column(db.Integer)
    status = db.Column(db.String(50))


# ----------------------------
# INIT
# ----------------------------
with app.app_context():
    db.create_all()

    if Foerderung.query.count() == 0:
        db.session.add_all([
            Foerderung(
                name="BAföG",
                beschreibung="Finanzielle Unterstützung für Studierende",
                zielgruppe="student",
                min_einkommen=0,
                max_einkommen=30000,
                hoehe="bis 934€ / Monat"
            ),
            Foerderung(
                name="Weiterbildungsbonus",
                beschreibung="Förderung für berufliche Weiterbildung",
                zielgruppe="arbeitnehmer",
                min_einkommen=0,
                max_einkommen=50000,
                hoehe="bis 2000€"
            )
        ])
        db.session.commit()


# ----------------------------
# UI TEMPLATE
# ----------------------------
BASE_HTML = """
<html>
<head>
    <title>Förderfinder</title>
    <style>
        body { font-family: Arial; max-width: 900px; margin: 40px auto; }
        .card { border:1px solid #ddd; padding:15px; margin:10px 0; border-radius:8px; }
        .btn { padding:10px; background:black; color:white; border:none; }
    </style>
</head>
<body>
<h1>💸 Förderfinder</h1>
{{content}}
</body>
</html>
"""


# ----------------------------
# LOGIN
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        typ = request.form.get("typ")
        einkommen = int(request.form.get("einkommen"))

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(email=email, typ=typ, einkommen=einkommen)
            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id
        return redirect("/dashboard")

    content = """
    <h2>Login</h2>
    <form method="post">
        <input name="email" placeholder="Email" required><br><br>

        <select name="typ">
            <option value="student">Student</option>
            <option value="arbeitnehmer">Arbeitnehmer</option>
        </select><br><br>

        <input name="einkommen" type="number" placeholder="Einkommen"><br><br>

        <button class="btn">Weiter</button>
    </form>
    """

    return render_template_string(BASE_HTML, content=content)


# ----------------------------
# DASHBOARD
# ----------------------------
@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect("/login")

    user = User.query.get(session["user_id"])

    foerderungen = Foerderung.query.filter(
        Foerderung.zielgruppe == user.typ,
        Foerderung.min_einkommen <= user.einkommen,
        Foerderung.max_einkommen >= user.einkommen
    ).all()

    content = f"<p>👤 {user.email} | <a href='/logout'>Logout</a></p>"
    content += "<h2>Passende Förderungen</h2>"

    for f in foerderungen:
        content += f"""
        <div class="card">
            <h3>{f.name}</h3>
            <p>{f.beschreibung}</p>
            <p><b>{f.hoehe}</b></p>

            <form method="post" action="/apply/{f.id}">
                <button class="btn">Jetzt beantragen</button>
            </form>
        </div>
        """

    content += "<h2>Meine Anträge</h2>"

    antraege = Antrag.query.filter_by(user_id=user.id).all()

    for a in antraege:
        f = Foerderung.query.get(a.foerderung_id)
        content += f"<p>{f.name} → {a.status}</p>"

    return render_template_string(BASE_HTML, content=content)


# ----------------------------
# APPLY
# ----------------------------
@app.route("/apply/<int:id>", methods=["POST"])
def apply(id):
    if not session.get("user_id"):
        return redirect("/login")

    antrag = Antrag(
        user_id=session["user_id"],
        foerderung_id=id,
        status="eingereicht"
    )

    db.session.add(antrag)
    db.session.commit()

    return redirect("/dashboard")


# ----------------------------
# LOGOUT
# ----------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")