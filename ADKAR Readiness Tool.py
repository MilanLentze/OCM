# ADKAR Readiness Tool v2.0 met Score- én Type-Verandering Analyse

import streamlit as st
import json
from fpdf import FPDF
import tempfile

# ====== Functies per ADKAR-domein =======

ADKAR_DOMAINS = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]
CHANGE_TYPES = ["proces", "technologie", "structuur", "cultuur"]

# Matrix met gedragsfeedback per domein, score en type verandering
FEEDBACK_MATRIX = {
    "Awareness": {
        (1.0, 1.9): {
            "proces": ("Volledige onwetendheid of verwarring", "Geen communicatie, vaagheid, overload", "Visuele storytelling, urgentiecampagnes, leiderschapscascade"),
            "technologie": ("Technologische verwarring of geen notie", "Tool-overload of vakjargon", "Visualisatie van impact, directe gebruikerscases"),
            "structuur": ("Onwetend over herstructurering", "Geen uitleg over impact op rol", "Simpele uitlegstructuur, casussen per afdeling"),
            "cultuur": ("Geen idee van cultuurverandering", "Abstract taalgebruik, geen koppeling", "Voorbeelden, waarde-workshops, informele verhalen")
        },
        (2.0, 2.9): {
            "proces": ("Weinig tot oppervlakkig begrip", "Te algemene uitleg, misconnectie met werkpraktijk", "Context-specifieke voorbeelden, vertaalsessies op teamniveau"),
            "technologie": ("Weten dat iets verandert, maar niet waarom", "Tool gepusht zonder nut te tonen", "Live demo's, voorbeelden van peers"),
            "structuur": ("Vaag gevoel dat iets verandert", "Geen koppeling met dagelijkse praktijk", "Structuurschema's met impact per team"),
            "cultuur": ("Ongeïnspireerd, passieve houding", "Verandering voelt als managementverhaal", "Dialoog over waarden, verhalen van koplopers")
        },
        (3.0, 3.9): {
            "proces": ("Begrip aanwezig maar niet overtuigend", "Info ontvangen maar geen verbinding", "Dialoogsessies, ‘wat betekent dit voor mij?’ sessies"),
            "technologie": ("Snapt nut maar voelt het nog niet", "Nog geen vertrouwen in gebruiksgemak", "Framing via persoonlijke winst, peer influence"),
            "structuur": ("Redelijk begrip van herstructurering", "Gebrek aan urgentie", "Verhalen van anderen, strategische kadering"),
            "cultuur": ("Ziet het nut, maar nog geen betrokkenheid", "Verwarring over gedrag", "Gedragsscripts, praktische voorbeelden")
        },
        (4.0, 5.0): {
            "proces": ("Helder en geaccepteerd waarom het nodig is", "Transparante communicatie, heldere richting", "Storytelling delen, versterken via informele netwerken"),
            "technologie": ("Duidelijk waarom tools nodig zijn", "Tool sluit aan bij toekomstvisie", "Ambassadeurschap stimuleren"),
            "structuur": ("Helderheid over herstructurering en doelen", "Strategische connectie gemaakt", "Laat teams zelf mee ontwerpen"),
            "cultuur": ("Voelt zich verbonden met de gewenste cultuur", "Herkenning in waarden en gedrag", "Cultuurdragers versterken, storytelling")
        }
    },
    # De overige domeinen (Desire, Knowledge, Ability, Reinforcement) worden op dezelfde manier ingevoegd
}

# ====== Interface =======
st.title("ADKAR Readiness Analyse v2.0")
st.markdown("Voer per domein een score in en selecteer het type verandering.")

results = {}

for domain in ADKAR_DOMAINS:
    st.subheader(domain)
    score = st.slider(f"{domain} score", 1.0, 5.0, step=0.1)
    change_type = st.selectbox(f"Type verandering voor {domain}", CHANGE_TYPES, key=domain)

    # Zoek feedback
    feedback = ("", "", "")
    for (low, high), types in FEEDBACK_MATRIX[domain].items():
        if low <= score <= high:
            feedback = types.get(change_type, ("", "", ""))
            break

    st.markdown(f"**Gedragssignaal:** {feedback[0]}")
    st.markdown(f"**Mogelijke oorzaak:** {feedback[1]}")
    st.markdown(f"**Aanpak/interventie:** {feedback[2]}")

    results[domain] = {
        "score": score,
        "type": change_type,
        "feedback": {
            "signal": feedback[0],
            "cause": feedback[1],
            "intervention": feedback[2]
        }
    }

# ====== PDF export functie =======
def generate_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="ADKAR Readiness Analyse Resultaat", ln=True, align='C')
    pdf.ln(10)

    for domain, data in results.items():
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt=f"{domain}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, txt=f"Score: {data['score']}\nType: {data['type']}\nGedragssignaal: {data['feedback']['signal']}\nOorzaak: {data['feedback']['cause']}\nInterventie: {data['feedback']['intervention']}")
        pdf.ln(5)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file

# ====== Download knoppen =======
if st.button("Download resultaat als PDF"):
    pdf_file = generate_pdf(results)
    with open(pdf_file.name, "rb") as f:
        st.download_button("Klik hier om PDF te downloaden", f, file_name="adkar_resultaat.pdf", mime="application/pdf")

if st.button("Download resultaat als JSON"):
    st.download_button(
        label="Klik hier om te downloaden",
        data=json.dumps(results, indent=2),
        file_name="adkar_resultaat.json",
        mime="application/json"
    )
