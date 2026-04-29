from flask import Flask
import os

app = Flask(__name__)

# ----------------------------
# DATEN MIT TAGS
# ----------------------------
foerderungen = [
    {
        "name": "BAföG",
        "beschreibung": "Finanzielle Unterstützung für Studierende.",
        "zielgruppe": ["student"],
        "voraussetzungen": [
            "Im Studium oder schulischer Ausbildung",
            "Unter 45 Jahre",
            "Geringes Einkommen"
        ],
        "hoehe": "Bis zu 934€ monatlich"
    },
    {
        "name": "Wohngeld",
        "beschreibung": "Zuschuss zur Miete.",
        "zielgruppe": ["alle"],
        "voraussetzungen": [
            "Eigene Wohnung",
            "Geringes Einkommen"
        ],
        "hoehe": "Abhängig von Einkommen"
    },
    {
        "name": "Kindergeld",
        "beschreibung": "Monatliche Zahlung für Familien.",
        "zielgruppe": ["familie"],
        "voraussetzungen": [
            "Unter 25 Jahre (bei Ausbildung)",
        ],
        "hoehe": "250€ monatlich"
    },
    {
        "name": "Aufstiegs-BAföG",
        "beschreibung": "Förderung für berufliche Weiterbildung.",
        "zielgruppe": ["azubi", "beruf"],
        "voraussetzungen": [
            "Weiterbildung oder Meisterkurs",
        ],
        "hoehe": "Zuschuss + Darlehen"
    }
]


# ----------------------------
# HOME
# ----------------------------
@app.route("/")
def home():
    html = """
    <html>
    <head>
        <title>Förderungen Übersicht</title>

        <style>
            body { font-family: Arial; max-width: 900px; margin: 40px auto; }
            .card { border:1px solid #ccc; padding:15px; margin:10px 0; border-radius:8px; }
            input, select { padding:10px; margin:10px 0; width:100%; }
        </style>

        <script>
        function filterCards() {
            let input = document.getElementById("search").value.toLowerCase();
            let filter = document.getElementById("filter").value;
            let cards = document.getElementsByClassName("card");

            for (let i = 0; i < cards.length; i++) {
                let text = cards[i].innerText.toLowerCase();
                let tag = cards[i].getAttribute("data-tag");

                let matchText = text.includes(input);
                let matchFilter = (filter === "alle" || tag.includes(filter));

                if (matchText && matchFilter) {
                    cards[i].style.display = "block";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }
        </script>

    </head>

    <body>

        <h1>💸 Förderungen Finder</h1>

        <input id="search" onkeyup="filterCards()" placeholder="🔍 Suche...">

        <select id="filter" onchange="filterCards()">
            <option value="alle">Alle</option>
            <option value="student">Student</option>
            <option value="azubi">Azubi</option>
            <option value="familie">Familie</option>
            <option value="beruf">Berufstätig</option>
        </select>
    """

    for f in foerderungen:
        tags = " ".join(f["zielgruppe"])

        html += f"""
        <div class="card" data-tag="{tags}">
            <h2>{f['name']}</h2>
            <p>{f['beschreibung']}</p>
            <p><b>Höhe:</b> {f['hoehe']}</p>

            <ul>
        """

        for v in f["voraussetzungen"]:
            html += f"<li>{v}</li>"

        html += "</ul></div>"

    html += "</body></html>"

    return html


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)