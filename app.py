from flask import Flask, request, send_file
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from markupsafe import escape
import urllib.parse

app = Flask(__name__)


# ----------------------------
# LOGIK: FÖRDERUNGEN
# ----------------------------
def check_bafoeg(age, status, income):
    if status == "student" and age < 45 and income < 1500:
        return ("hoch", "Du erfüllst die wichtigsten Voraussetzungen für BAföG.")
    elif status == "student" and income < 2500:
        return ("mittel", "Teilweise Voraussetzungen erfüllt.")
    return ("gering", "BAföG aktuell eher unwahrscheinlich.")


def check_wohngeld(living, income):
    if living in ["allein", "wg"] and income < 2000:
        return ("hoch", "Wohngeld sehr wahrscheinlich möglich.")
    elif income < 3000:
        return ("mittel", "Wohngeld könnte möglich sein.")
    return ("gering", "Wohngeld eher unwahrscheinlich.")


def check_kindergeld(age):
    if age < 25:
        return ("hoch", "Kindergeld steht dir wahrscheinlich zu.")
    return ("gering", "Kein Anspruch auf Kindergeld.")


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    return """
    <html>
    <body style="font-family: Arial; max-width:700px; margin:40px auto;">
    
    <h1>🎯 Förderungs-Checker</h1>
    <p>Finde heraus, welche staatlichen Förderungen du bekommen kannst.</p>

    <form action="/result" method="post">
        <input name="age" placeholder="Alter" required><br><br>

        <select name="status">
            <option value="student">Student</option>
            <option value="ausbildung">Ausbildung</option>
            <option value="arbeit">Arbeit</option>
        </select><br><br>

        <input name="income" placeholder="Monatliches Einkommen (€)" required><br><br>

        <select name="living">
            <option value="bei_eltern">Bei Eltern</option>
            <option value="allein">Allein</option>
            <option value="wg">WG</option>
        </select><br><br>

        <button>Check starten</button>
    </form>

    </body>
    </html>
    """


# ----------------------------
# RESULT
# ----------------------------
@app.route("/result", methods=["POST"])
def result():

    try:
        age = int(request.form.get("age"))
        income = float(request.form.get("income").replace(",", "."))
    except:
        return "Eingaben ungültig"

    status = request.form.get("status")
    living = request.form.get("living")

    # Förderungen prüfen
    results = []

    b = check_bafoeg(age, status, income)
    results.append(("BAföG", b))

    w = check_wohngeld(living, income)
    results.append(("Wohngeld", w))

    k = check_kindergeld(age)
    results.append(("Kindergeld", k))

    # HTML bauen
    output = ""
    text_for_pdf = "FÖRDERUNGS-CHECK\n\n"

    for name, (level, text) in results:
        color = {"hoch": "green", "mittel": "orange", "gering": "red"}[level]

        output += f"""
        <div style="border:1px solid #ccc; padding:15px; margin:10px 0;">
            <h3>{name}</h3>
            <p style="color:{color}; font-weight:bold;">{level.upper()}</p>
            <p>{text}</p>
        </div>
        """

        text_for_pdf += f"{name}: {level.upper()}\n{text}\n\n"

    safe_output = escape(text_for_pdf)
    encoded = urllib.parse.quote(text_for_pdf)

    return f"""
    <html>
    <body style="font-family: Arial; max-width:700px; margin:40px auto;">

    <h2>🔍 Deine Ergebnisse</h2>

    {output}

    <a href="/download?data={encoded}">
        <button>📄 Als PDF herunterladen</button>
    </a>

    <br><br>
    <a href="/">Neu starten</a>

    </body>
    </html>
    """


# ----------------------------
# PDF DOWNLOAD
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

    return send_file(buffer, as_attachment=True, download_name="foerderung.pdf")


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)