from flask import Flask, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ----------------------------
# CONFIG (Render ENV)
# ----------------------------
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

database_url = os.environ.get("DATABASE_URL", "sqlite:///foerderungen.db")
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

# ----------------------------
# ROUTES
# ----------------------------
@app.route("/")
def home():
    return "<h1>🚀 Förderfinder läuft auf Render!</h1><a href='/login'>Login</a>"


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

    return """
    <h2>Login</h2>
    <form method="post">
        <input name="email" placeholder="Email"><br>
        <select name="typ">
            <option value="student">Student</option>
            <option value="arbeitnehmer">Arbeitnehmer</option>
        </select><br>
        <input name="einkommen" type="number"><br>
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

    html = f"<h1>Willkommen {user.email}</h1>"

    for f in passende:
        html += f"""
        <div>
            <h3>{f.name}</h3>
            <p>{f.hoehe}</p>
            <form method="post" action="/apply/{f.id}">
                <button>Beantragen</button>
            </form>
        </div>
        """

    return html


@app.route("/apply/<int:id>", methods=["POST"])
def apply(id):
    antrag = Antrag(
        user_id=session["user_id"],
        foerderung_id=id,
        status="eingereicht"
    )

    db.session.add(antrag)
    db.session.commit()

    return redirect("/dashboard")


# WICHTIG: KEIN app.run() für Render!