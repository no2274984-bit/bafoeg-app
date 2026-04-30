import os

# ----------------------------
# SAFE IMPORTS (verhindert Crash)
# ----------------------------
try:
    from flask import Flask, request, redirect, session
    from flask_sqlalchemy import SQLAlchemy
except ImportError as e:
    raise Exception(
        "❌ Fehlende Packages! Stelle sicher, dass requirements.txt korrekt ist.\n"
        "Benötigt: Flask, Flask-SQLAlchemy, gunicorn"
    ) from e

app = Flask(__name__)

# ----------------------------
# CONFIG
# ----------------------------
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

database_url = os.environ.get("DATABASE_URL")

# Fallback für lokal (Render nutzt PostgreSQL)
if not database_url:
    database_url = "sqlite:///foerderungen.db"

# Fix für PostgreSQL URL (Render)
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
# INIT DB
# ----------------------------
with app.app_context():
    db.create_all()

    # Seed Daten (nur wenn leer)
    if Foerderung.query.count() == 0:
        db.session.add(Foerderung(
            name="BAföG",
            beschreibung="Förderung für Studierende",
            zielgruppe="student",
            min_einkommen=0,
            max_einkommen=30000,
            hoehe="bis 934€ monatlich"
        ))
        db.session.commit()


# ----------------------------
# ROUTES
# ----------------------------
@app.route("/")
def home():
    return """
    <h1>💸 Förderfinder läuft</h1>
    <a href='/login'>Login</a>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            email = request.form.get("email")
            typ = request.form.get("typ")
            einkommen = int(request.form.get("einkommen"))
        except:
            return "❌ Eingaben ungültig"

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(email=email, typ=typ, einkommen=einkommen)
            db.session.add(user)
            db.session.commit()

        session["user_id"] = user.id
        return redirect("/dashboard")

    return """
    <h2>Login</h2>
    <form method="post">
        <input name="email" placeholder="Email" required><br>
        <select name="typ">
            <option value="student">Student</option>
            <option value="arbeitnehmer">Arbeitnehmer</option>
        </select><br>
        <input name="einkommen" type="number" required><br>
        <button>Login</button>
    </form>
    """


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect("/login")

    user = User.query.get(session["user_id"])

    passende = Foerderung.query.filter(
        Foerderung.zielgruppe == user.typ,
        Foerderung.min_einkommen <= user.einkommen,
        Foerderung.max_einkommen >= user.einkommen
    ).all()

    html = f"<h1>👤 {user.email}</h1>"

    for f in passende:
        html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:10px;">
            <h3>{f.name}</h3>
            <p>{f.beschreibung}</p>
            <p><b>{f.hoehe}</b></p>

            <form method="post" action="/apply/{f.id}">
                <button>Beantragen</button>
            </form>
        </div>
        """

    return html


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
# LOCAL ONLY START
# ----------------------------
if __name__ == "__main__":
    print("🚀 Starte lokal...")
    app.run(host="0.0.0.0", port=10000)