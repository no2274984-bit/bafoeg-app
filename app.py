from flask import Flask, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

database_url = os.environ.get("DATABASE_URL", "sqlite:///foerderungen.db")

# Fix für Render PostgreSQL
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


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "<h1>🚀 App läuft!</h1>"


# KEIN app.run() für Render!