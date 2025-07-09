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
    "Desire": {
        (1.0, 1.9): {
            "proces": ("Actieve weerstand of passieve sabotering", "Geen zeggenschap over procesverandering", "Invloed geven, weerstand normaliseren"),
            "technologie": ("Technofobie of afhakend gedrag", "Angst voor controleverlies of fouten", "Peer influence, laten ervaren van gemak"),
            "structuur": ("Ontkenning of terugtrekken", "Onzekerheid over toekomstpositie", "Transparant zijn over implicaties en keuzeruimte"),
            "cultuur": ("Cynisme of terugverlangen naar oude cultuur", "Verlies van identiteit of waarden", "Erkenning van emoties, dialoog op waarden")
        },
        (2.0, 2.9): {
            "proces": ("Afstandelijke houding", "Niet overtuigd van nut of urgentie", "Betrekken bij herontwerp, show quick wins"),
            "technologie": ("Sceptisch of onverschillig", "Geen vertrouwen in nut van tool", "Koppelen aan werkplezier of gemak"),
            "structuur": ("Passief volgen", "Zien reorganisatie als opgelegd", "Verbind met persoonlijke impact en groeikansen"),
            "cultuur": ("Neutraal, niet betrokken", "Verandering voelt extern of abstract", "Inspirerende verhalen en leiderschap zichtbaar maken")
        },
        (3.0, 3.9): {
            "proces": ("Voorzichtig meewerkend", "Nog weinig emotionele connectie", "Successen delen, ruimte voor invloed geven"),
            "technologie": ("Mee eens, maar geen ambassadeur", "Onzekerheid of gewenning ontbreekt", "Gamified adoptie, ervaringssessies"),
            "structuur": ("Mee eens mits goed uitgelegd", "Er zijn zorgen, maar wel openheid", "Visie koppelen aan dagelijkse rol"),
            "cultuur": ("Mee in woorden, nog niet in gedrag", "Onzeker over nieuwe normen", "Voorbeelden zichtbaar maken, belonen gewenst gedrag")
        },
        (4.0, 5.0): {
            "proces": ("Actieve medewerking en initiatief", "Herkenning van waarde en nut", "Geef podium, rolmodelgedrag stimuleren"),
            "technologie": ("Promoot tool spontaan", "Ervaring positief, wil delen", "Laat ambassadeurs trainen en supporten"),
            "structuur": ("Draagt reorganisatie", "Snapt strategisch nut", "Laat hen nieuwe structuren co-designen"),
            "cultuur": ("Belichaamt nieuwe cultuur", "Verbinding met waarden en doelen", "Versterk met storytelling en peer influence")
        }
    },
    "Knowledge": {},
    "Ability": {},
    "Reinforcement": {}
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
    if domain in FEEDBACK_MATRIX:
        for (low, high), types in FEEDBACK_MATRIX.get(domain, {}).items():
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
