from flask import Flask, request, send_file
import os
from markupsafe import escape
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>BAföG Assistent</title>
        <style>
            body { font-family: Arial; max-width: 650px; margin: 50px auto; }
            input { width: 100%; padding: 10px; margin: 6px 0; }
            button { width: 100%; padding: 12px; background: black; color: white; border: none; }
        </style>
    </head>
    <body>

        <h1>BAföG Assistent</h1>

        <form action="/submit" method="post">
            <input name="age" placeholder="Alter *" required>
            <input name="study" placeholder="Studiengang *" required>
            <input name="semester" placeholder="Semester *" required>

            <input name="job" placeholder="Nebenjob (ja/nein)">
            <input name="income" placeholder="Einkommen (€)">
            <input name="living" placeholder="Wohnsituation">

            <button type="submit">Antrag erstellen</button>
        </form>

    </body>
    </html>
    """


# ----------------------------
# SUBMIT
# ----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    age = request.form.get("age")
    study = request.form.get("study")
    semester = request.form.get("semester")
    job = (request.form.get("job") or "").lower()
    income = request.form.get("income") or ""
    living = request.form.get("living") or "nicht angegeben"

    if not age or not study or not semester:
        return "Pflichtfelder fehlen"

    try:
        age = int(age)
    except:
        return "Alter muss Zahl sein"

    job_text = "Nebenjob: Ja" if job in ["ja", "yes"] else "Nebenjob: Nein"

    if income:
        try:
            income_val = float(income.replace(",", "."))
            income_text = f"Einkommen: {income_val:.2f} €"
        except:
            return "Einkommen ungültig"
    else:
        income_text = "Kein Einkommen angegeben"

    result = f"""
BAföG ANTRAG

Alter: {age}
Studium: {study}
Semester: {semester}

{job_text}
{income_text}

Wohnsituation: {living}
"""

    safe_result = escape(result)

    # Übergabe an Download via Query (einfach & stateless)
    import urllib.parse
    encoded = urllib.parse.quote(result)

    return f"""
    <html>
    <body style="font-family: Arial; max-width: 700px; margin: 40px auto;">

        <h2>Dein Antrag</h2>

        <pre>{safe_result}</pre>

        <a href="/download?data={encoded}">
            <button>📄 Als PDF herunterladen</button>
        </a>

        <br><br>
        <a href="/">Zurück</a>

    </body>
    </html>
    """


# ----------------------------
# DOWNLOAD (IN MEMORY)
# ----------------------------
@app.route("/download")
def download():
    data = request.args.get("data", "")

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    y = 800
    for line in data.split("\n"):
        c.drawString(50, y, line)
        y -= 20

    c.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="bafoeg_antrag.pdf",
        mimetype="application/pdf"
    )


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render nutzt oft 10000
    app.run(host="0.0.0.0", port=port)