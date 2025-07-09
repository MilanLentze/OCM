# Verbeterde ADKAR Scan Tool met visuele UI upgrades

import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import json
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="ADKAR Scan Tool", layout="wide")
st.markdown("""
    <style>
    summary {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    </style>
""", unsafe_allow_html=True)

# === Constantes ===
ADKAR_DOMAINS = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]
CHANGE_TYPES = ["Proces", "Technologie", "Structuur", "Cultuur"]
DOMAIN_COLORS = {
    "Awareness": "#FFA07A",
    "Desire": "#F4A460",
    "Knowledge": "#87CEFA",
    "Ability": "#90EE90",
    "Reinforcement": "#DDA0DD"
}

# Matrix met gedragsfeedback per domein, score en type verandering
FEEDBACK_MATRIX = {
    "Awareness": {
        (1.0, 1.9): {
            "Proces": ("Volledige onwetendheid of verwarring", "Geen communicatie, vaagheid, overload", "Visuele storytelling, urgentiecampagnes, leiderschapscascade"),
            "Technologie": ("Technologische verwarring of geen notie", "Tool-overload of vakjargon", "Visualisatie van impact, directe gebruikerscases"),
            "Structuur": ("Onwetend over herstructurering", "Geen uitleg over impact op rol", "Simpele uitlegstructuur, casussen per afdeling"),
            "Cultuur": ("Geen idee van cultuurverandering", "Abstract taalgebruik, geen koppeling", "Voorbeelden, waarde-workshops, informele verhalen")
        },
        (2.0, 2.9): {
            "Proces": ("Weinig tot oppervlakkig begrip", "Te algemene uitleg, misconnectie met werkpraktijk", "Context-specifieke voorbeelden, vertaalsessies op teamniveau"),
            "Technologie": ("Weten dat iets verandert, maar niet waarom", "Tool gepusht zonder nut te tonen", "Live demo's, voorbeelden van peers"),
            "Structuur": ("Vaag gevoel dat iets verandert", "Geen koppeling met dagelijkse praktijk", "Structuurschema's met impact per team"),
            "Cultuur": ("Ongeïnspireerd, passieve houding", "Verandering voelt als managementverhaal", "Dialoog over waarden, verhalen van koplopers")
        },
        (3.0, 3.9): {
            "Proces": ("Begrip aanwezig maar niet overtuigend", "Info ontvangen maar geen verbinding", "Dialoogsessies, ‘wat betekent dit voor mij?’ sessies"),
            "Technologie": ("Snapt nut maar voelt het nog niet", "Nog geen vertrouwen in gebruiksgemak", "Framing via persoonlijke winst, peer influence"),
            "Structuur": ("Redelijk begrip van herstructurering", "Gebrek aan urgentie", "Verhalen van anderen, strategische kadering"),
            "Cultuur": ("Ziet het nut, maar nog geen betrokkenheid", "Verwarring over gedrag", "Gedragsscripts, praktische voorbeelden")
        },
        (4.0, 5.0): {
            "Proces": ("Helder en geaccepteerd waarom het nodig is", "Transparante communicatie, heldere richting", "Storytelling delen, versterken via informele netwerken"),
            "Technologie": ("Duidelijk waarom tools nodig zijn", "Tool sluit aan bij toekomstvisie", "Ambassadeurschap stimuleren"),
            "Structuur": ("Helderheid over herstructurering en doelen", "Strategische connectie gemaakt", "Laat teams zelf mee ontwerpen"),
            "Cultuur": ("Voelt zich verbonden met de gewenste cultuur", "Herkenning in waarden en gedrag", "Cultuurdragers versterken, storytelling")
        }
    },
    "Desire": {
        (1.0, 1.9): {
            "Proces": ("Actieve weerstand of passieve sabotering", "Geen zeggenschap over procesverandering", "Invloed geven, weerstand normaliseren"),
            "Technologie": ("Technofobie of afhakend gedrag", "Angst voor controleverlies of fouten", "Peer influence, laten ervaren van gemak"),
            "Structuur": ("Ontkenning of terugtrekken", "Onzekerheid over toekomstpositie", "Transparant zijn over implicaties en keuzeruimte"),
            "Cultuur": ("Cynisme of terugverlangen naar oude cultuur", "Verlies van identiteit of waarden", "Erkenning van emoties, dialoog op waarden")
        },
        (2.0, 2.9): {
            "Proces": ("Afstandelijke houding", "Niet overtuigd van nut of urgentie", "Betrekken bij herontwerp, show quick wins"),
            "Technologie": ("Sceptisch of onverschillig", "Geen vertrouwen in nut van tool", "Koppelen aan werkplezier of gemak"),
            "Structuur": ("Passief volgen", "Zien reorganisatie als opgelegd", "Verbind met persoonlijke impact en groeikansen"),
            "Cultuur": ("Neutraal, niet betrokken", "Verandering voelt extern of abstract", "Inspirerende verhalen en leiderschap zichtbaar maken")
        },
        (3.0, 3.9): {
            "Proces": ("Voorzichtig meewerkend", "Nog weinig emotionele connectie", "Successen delen, ruimte voor invloed geven"),
            "Technologie": ("Mee eens, maar geen ambassadeur", "Onzekerheid of gewenning ontbreekt", "Gamified adoptie, ervaringssessies"),
            "Structuur": ("Mee eens mits goed uitgelegd", "Er zijn zorgen, maar wel openheid", "Visie koppelen aan dagelijkse rol"),
            "Cultuur": ("Mee in woorden, nog niet in gedrag", "Onzeker over nieuwe normen", "Voorbeelden zichtbaar maken, belonen gewenst gedrag")
        },
        (4.0, 5.0): {
            "Proces": ("Actieve medewerking en initiatief", "Herkenning van waarde en nut", "Geef podium, rolmodelgedrag stimuleren"),
            "Technologie": ("Promoot tool spontaan", "Ervaring positief, wil delen", "Laat ambassadeurs trainen en supporten"),
            "Structuur": ("Draagt reorganisatie", "Snapt strategisch nut", "Laat hen nieuwe structuren co-designen"),
            "Cultuur": ("Belichaamt nieuwe cultuur", "Verbinding met waarden en doelen", "Versterk met storytelling en peer influence")
        }
    },
    "Knowledge": {
    (1.0, 1.9): {
        "Proces": ("Geen idee wat ik moet doen", "Geen uitleg over nieuwe werkwijze", "Stap-voor-stap handleiding, live instructie"),
        "Technologie": ("Verdwaald in tool of systeem", "Geen onboarding, te technisch", "Demo’s, dummy accounts, visuele gidsen"),
        "Structuur": ("Onbegrip over nieuwe rollen/functies", "Geen uitleg over gevolgen", "Schema’s met voorbeeldtaken, uitleg-sessies"),
        "Cultuur": ("Weet niet welk gedrag gewenst is", "Verandering blijft abstract", "Gedragsexamples, waardenposter, interactieve sessies")
    },
    (2.0, 2.9): {
        "Proces": ("Oppervlakkig begrip van nieuwe werkwijze", "Algemene uitleg, geen concrete voorbeelden", "Werksimulaties, buddy-systemen"),
        "Technologie": ("Beperkt begrip van systeem", "Training gemist of vergeten", "Refresher video’s, just-in-time tips"),
        "Structuur": ("Basiskennis van structuur", "Slecht afgestemde communicatie", "Interactieve organigrammen, impactkaarten"),
        "Cultuur": ("Herhaalt termen maar zonder inzicht", "Geen vertaling naar gedrag", "Verhalende voorbeelden, groepsdiscussies")
    },
    (3.0, 3.9): {
        "Proces": ("Weet wat moet, maar onzeker over toepassing", "Te weinig oefening", "Practice labs, Q&A sessies"),
        "Technologie": ("Kan navigeren maar mist finesse", "Ingewikkelde functies onbekend", "How-to’s, advanced tips door peers"),
        "Structuur": ("Redelijk inzicht in impact", "Twijfel over positionering", "Feedbackmomenten, visuele rolduiding"),
        "Cultuur": ("Snapt kernwaarden maar twijfelt over toepassing", "Onzeker over verwachting", "Gedragssimulaties, groepsreflectie")
    },
    (4.0, 5.0): {
        "Proces": ("Volledig begrip van nieuwe werkwijze", "Trainingen en tools waren effectief", "Laat medewerkers anderen trainen"),
        "Technologie": ("Comfortabel met systeemgebruik", "Goede onboarding", "Laat medewerkers tips delen"),
        "Structuur": ("Volledig inzicht in nieuwe structuur", "Heldere communicatie", "Gebruik als sparringpartner voor anderen"),
        "Cultuur": ("Begrijpt en vertaalt cultuurwaarden", "Heldere normcommunicatie", "Rolmodel, gedrag in communicatie verankeren")
    }
    },
    "Ability": {
    (1.0, 1.9): {
        "Proces": ("Fouten, frustratie of vermijding", "Geen ruimte om te oefenen", "Mentoring, tijd om te leren"),
        "Technologie": ("Tool wordt vermeden of fout gebruikt", "Te complex, geen begeleiding", "Simpele taken eerst, schermopnames gebruiken"),
        "Structuur": ("Niet in staat nieuwe rol op te pakken", "Geen transitie-ondersteuning", "Schaduwrollen, observatie-onboarding"),
        "Cultuur": ("Onzeker of inconsequent gedrag", "Angst voor oordeel", "Feedback in veilige setting, rollenspellen")
    },
    (2.0, 2.9): {
        "Proces": ("Pogingen, maar onzeker of onvolledig", "Gebrek aan oefentijd", "Werkplekcoaching, duidelijke prioriteiten"),
        "Technologie": ("Beperkte vaardigheid", "Verouderde instructies, weinig herhaling", "Praktische support via helpdesk of peers"),
        "Structuur": ("Deeltaken lukken, maar mist overzicht", "Nieuwe rol niet duidelijk afgebakend", "Stapplan per week, daily check-ins"),
        "Cultuur": ("Probeert zich aan te passen, maar onzeker", "Nieuwe normen nog niet eigen", "Co-coaching, voorbeeldgedrag van peers")
    },
    (3.0, 3.9): {
        "Proces": ("Past het toe met enige hulp", "Ervaring groeit", "Verantwoordelijkheid geven, feedbackloops"),
        "Technologie": ("Zelfstandig met tool, af en toe hulp nodig", "Onzeker bij uitzonderingen", "Casussen oefenen, advanced training"),
        "Structuur": ("Kan nieuwe rol grotendeels aan", "Mist soms vertrouwen", "Peer validation, complimenten voor voortgang"),
        "Cultuur": ("Vertoont gedrag grotendeels passend", "Nog twijfel in groep", "Feedback door team, positieve beloning")
    },
    (4.0, 5.0): {
        "Proces": ("Zelfverzekerd en foutloos toepassen", "Oefening en ervaring aanwezig", "Laat hen als coach optreden"),
        "Technologie": ("Effectief en efficiënt in toolgebruik", "Volledige vaardigheid", "Vraag hen input voor optimalisatie"),
        "Structuur": ("Kan rol uitvoeren en collega’s ondersteunen", "Heldere positionering", "Gebruik als mentor of buddy"),
        "Cultuur": ("Gedrag vanzelfsprekend en congruent", "Nieuwe cultuur geïnternaliseerd", "Laat voorbeeld zijn voor nieuwe instroom")
    }
    },
    "Reinforcement": {
    (1.0, 1.9): {
        "Proces": ("Valt terug in oude routines", "Geen opvolging of monitoring", "Leiders aanspreken, successen zichtbaar maken"),
        "Technologie": ("Tool wordt verlaten", "Geen check-in of support", "Adoptie monitoren, reminders, follow-ups"),
        "Structuur": ("Vervalt in oude rolstructuur", "Geen verankering in beleid", "Formele updates, nieuwe verantwoordelijkheden borgen"),
        "Cultuur": ("Gedrag verwatert", "Leiders doen niet mee", "Gedrag zichtbaar maken, cultuurdragers aanspreken")
    },
    (2.0, 2.9): {
        "Proces": ("Soms juiste werkwijze, soms niet", "Inconsistentie in teams", "Teamreviews, korte check-ins"),
        "Technologie": ("Afhankelijk van persoon of team", "Geen supportstructuur", "Superusers installeren, interne FAQ’s"),
        "Structuur": ("Nieuwe structuur wordt soms genegeerd", "Gebrek aan leiderschapssupport", "Teamverantwoordelijkheid benadrukken"),
        "Cultuur": ("Wisselend gedrag", "Geen consequenties of beloning", "Waardering geven, sociale erkenning")
    },
    (3.0, 3.9): {
        "Proces": ("Grotendeels geborgd", "Nog risico bij drukte", "Blijvende reminders, standaardisering"),
        "Technologie": ("Consistent gebruik bij meerderheid", "Enkele afhakers", "Verhalen delen, nudging via peers"),
        "Structuur": ("Rol en structuur meestal geborgd", "Afhankelijk van teamlead", "Verantwoordelijkheid in team zichtbaar maken"),
        "Cultuur": ("Nieuwe normen worden gevolgd", "Nog onzeker in informele sfeer", "Erken gedrag, continue reflectie")
    },
    (4.0, 5.0): {
        "Proces": ("Verandering is standaardpraktijk", "Proces zit in het systeem", "Blijf belonen, deel good practices"),
        "Technologie": ("Toolgebruik vanzelfsprekend", "Volledige integratie", "Ambassadeurschap onderhouden"),
        "Structuur": ("Nieuwe structuur is de norm", "Teams functioneren soepel", "Gebruik voor nieuwe transities als referentie"),
        "Cultuur": ("Nieuwe cultuur gedragen door iedereen", "Gedrag is onbewust congruent", "Koester cultuurdragers, onboarding verankeren")
    }
}
}


st.title("📘 ADKAR Readiness Scan")
st.markdown("Beoordeel elk ADKAR-domein en ontvang gedragssignalen, oorzaken en aanbevelingen.")

results = {}

# 🔽 Type verandering bovenaan kiezen
change_type = st.selectbox("🔧 Kies het type verandering dat van toepassing is op alle domeinen:", CHANGE_TYPES)

# === Invoer per domein ===
for domain in ADKAR_DOMAINS:
    with st.expander(f"🔍 {domain}"):
        score = st.slider("", 1.0, 5.0, step=0.1, key=f"slider_{domain}")

        # 🧠 Bepaal juiste label op basis van score
        if 1.0 <= score <= 1.9:
            status_label = "🔴 Score: Zeer laag"
        elif 2.0 <= score <= 2.9:
            status_label = "🟠 Score: Laag"
        elif 3.0 <= score <= 3.9:
            status_label = "🟡 Score: Gemiddeld"
        elif 4.0 <= score <= 4.9:
            status_label = "🟢 Score: Sterk"
        else:
            status_label = "✅ Score: Uitstekend"

        # 🔍 Haal feedback op uit matrix
        feedback = ("", "", "")
        if domain in FEEDBACK_MATRIX:
            for (low, high), types in FEEDBACK_MATRIX[domain].items():
                if low <= score <= high:
                    feedback = types.get(change_type, ("", "", ""))
                    break

        # 💬 Toon alles netjes in HTML-box
        st.markdown(
    f"""
    <div style="padding: 1rem; background-color: #f9f9f9; border-radius: 8px;">
        <h5 style="margin-bottom: 0.8rem;">{domain} – {status_label}</h5>
        <p style="margin-bottom: 0.6rem;"><strong>🔢 Score:</strong> {score:.1f}</p>
        <p style="margin-bottom: 0.6rem;"><strong>🔧 Type verandering:</strong> {change_type.capitalize()}</p>
        <hr style="margin: 1rem 0;">
        <p style="margin-bottom: 0.8rem;"><strong>📍 Mogelijk gedragssignaal:</strong><br>{feedback[0]}</p>
        <p style="margin-bottom: 0.8rem;"><strong>💡 Mogelijke oorzaak:</strong><br>{feedback[1]}</p>
        <p style="margin-bottom: 0.8rem;"><strong>🛠️ Aanpak/interventie:</strong><br>{feedback[2]}</p>
    </div>
    """,
    unsafe_allow_html=True
)

        # Voeg toe aan resultaten
        results[domain] = {
            "score": score,
            "type": change_type,
            "feedback": {
                "signal": feedback[0],
                "cause": feedback[1],
                "intervention": feedback[2]
            }
        }

# === Gemiddelde Score ===
avg_score = round(np.mean([v["score"] for v in results.values()]), 2)
st.metric("Gemiddelde ADKAR-score", avg_score)

# === Radar Chart (Plotly) ===
st.subheader("📊 ADKAR Profieloverzicht")
labels = ADKAR_DOMAINS
scores = [results[d]["score"] for d in labels]
scores += scores[:1]
labels += labels[:1]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=scores,
    theta=labels,
    fill='toself',
    name='ADKAR Scores',
    line=dict(color='royalblue')
))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
    showlegend=False,
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# === PDF Export ===
def generate_pdf(results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="ADKAR Readiness Analyse", ln=True, align='C')
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

# === Downloadknoppen ===
col1, col2 = st.columns(2)
with col1:
    if st.button("📥 Download PDF"):
        pdf_file = generate_pdf(results)
        with open(pdf_file.name, "rb") as f:
            st.download_button("Klik hier om te downloaden", f, file_name="adkar_resultaat.pdf", mime="application/pdf")
