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
    "Knowledge": {
    (1.0, 1.9): {
        "proces": ("Geen idee wat ik moet doen", "Geen uitleg over nieuwe werkwijze", "Stap-voor-stap handleiding, live instructie"),
        "technologie": ("Verdwaald in tool of systeem", "Geen onboarding, te technisch", "Demo’s, dummy accounts, visuele gidsen"),
        "structuur": ("Onbegrip over nieuwe rollen/functies", "Geen uitleg over gevolgen", "Schema’s met voorbeeldtaken, uitleg-sessies"),
        "cultuur": ("Weet niet welk gedrag gewenst is", "Verandering blijft abstract", "Gedragsexamples, waardenposter, interactieve sessies")
    },
    (2.0, 2.9): {
        "proces": ("Oppervlakkig begrip van nieuwe werkwijze", "Algemene uitleg, geen concrete voorbeelden", "Werksimulaties, buddy-systemen"),
        "technologie": ("Beperkt begrip van systeem", "Training gemist of vergeten", "Refresher video’s, just-in-time tips"),
        "structuur": ("Basiskennis van structuur", "Slecht afgestemde communicatie", "Interactieve organigrammen, impactkaarten"),
        "cultuur": ("Herhaalt termen maar zonder inzicht", "Geen vertaling naar gedrag", "Verhalende voorbeelden, groepsdiscussies")
    },
    (3.0, 3.9): {
        "proces": ("Weet wat moet, maar onzeker over toepassing", "Te weinig oefening", "Practice labs, Q&A sessies"),
        "technologie": ("Kan navigeren maar mist finesse", "Ingewikkelde functies onbekend", "How-to’s, advanced tips door peers"),
        "structuur": ("Redelijk inzicht in impact", "Twijfel over positionering", "Feedbackmomenten, visuele rolduiding"),
        "cultuur": ("Snapt kernwaarden maar twijfelt over toepassing", "Onzeker over verwachting", "Gedragssimulaties, groepsreflectie")
    },
    (4.0, 5.0): {
        "proces": ("Volledig begrip van nieuwe werkwijze", "Trainingen en tools waren effectief", "Laat medewerkers anderen trainen"),
        "technologie": ("Comfortabel met systeemgebruik", "Goede onboarding", "Laat medewerkers tips delen"),
        "structuur": ("Volledig inzicht in nieuwe structuur", "Heldere communicatie", "Gebruik als sparringpartner voor anderen"),
        "cultuur": ("Begrijpt en vertaalt cultuurwaarden", "Heldere normcommunicatie", "Rolmodel, gedrag in communicatie verankeren")
    }
    },
    "Ability": {
    (1.0, 1.9): {
        "proces": ("Fouten, frustratie of vermijding", "Geen ruimte om te oefenen", "Mentoring, tijd om te leren"),
        "technologie": ("Tool wordt vermeden of fout gebruikt", "Te complex, geen begeleiding", "Simpele taken eerst, schermopnames gebruiken"),
        "structuur": ("Niet in staat nieuwe rol op te pakken", "Geen transitie-ondersteuning", "Schaduwrollen, observatie-onboarding"),
        "cultuur": ("Onzeker of inconsequent gedrag", "Angst voor oordeel", "Feedback in veilige setting, rollenspellen")
    },
    (2.0, 2.9): {
        "proces": ("Pogingen, maar onzeker of onvolledig", "Gebrek aan oefentijd", "Werkplekcoaching, duidelijke prioriteiten"),
        "technologie": ("Beperkte vaardigheid", "Verouderde instructies, weinig herhaling", "Praktische support via helpdesk of peers"),
        "structuur": ("Deeltaken lukken, maar mist overzicht", "Nieuwe rol niet duidelijk afgebakend", "Stapplan per week, daily check-ins"),
        "cultuur": ("Probeert zich aan te passen, maar onzeker", "Nieuwe normen nog niet eigen", "Co-coaching, voorbeeldgedrag van peers")
    },
    (3.0, 3.9): {
        "proces": ("Past het toe met enige hulp", "Ervaring groeit", "Verantwoordelijkheid geven, feedbackloops"),
        "technologie": ("Zelfstandig met tool, af en toe hulp nodig", "Onzeker bij uitzonderingen", "Casussen oefenen, advanced training"),
        "structuur": ("Kan nieuwe rol grotendeels aan", "Mist soms vertrouwen", "Peer validation, complimenten voor voortgang"),
        "cultuur": ("Vertoont gedrag grotendeels passend", "Nog twijfel in groep", "Feedback door team, positieve beloning")
    },
    (4.0, 5.0): {
        "proces": ("Zelfverzekerd en foutloos toepassen", "Oefening en ervaring aanwezig", "Laat hen als coach optreden"),
        "technologie": ("Effectief en efficiënt in toolgebruik", "Volledige vaardigheid", "Vraag hen input voor optimalisatie"),
        "structuur": ("Kan rol uitvoeren en collega’s ondersteunen", "Heldere positionering", "Gebruik als mentor of buddy"),
        "cultuur": ("Gedrag vanzelfsprekend en congruent", "Nieuwe cultuur geïnternaliseerd", "Laat voorbeeld zijn voor nieuwe instroom")
    }
    },
    "Reinforcement": {
    (1.0, 1.9): {
        "proces": ("Valt terug in oude routines", "Geen opvolging of monitoring", "Leiders aanspreken, successen zichtbaar maken"),
        "technologie": ("Tool wordt verlaten", "Geen check-in of support", "Adoptie monitoren, reminders, follow-ups"),
        "structuur": ("Vervalt in oude rolstructuur", "Geen verankering in beleid", "Formele updates, nieuwe verantwoordelijkheden borgen"),
        "cultuur": ("Gedrag verwatert", "Leiders doen niet mee", "Gedrag zichtbaar maken, cultuurdragers aanspreken")
    },
    (2.0, 2.9): {
        "proces": ("Soms juiste werkwijze, soms niet", "Inconsistentie in teams", "Teamreviews, korte check-ins"),
        "technologie": ("Afhankelijk van persoon of team", "Geen supportstructuur", "Superusers installeren, interne FAQ’s"),
        "structuur": ("Nieuwe structuur wordt soms genegeerd", "Gebrek aan leiderschapssupport", "Teamverantwoordelijkheid benadrukken"),
        "cultuur": ("Wisselend gedrag", "Geen consequenties of beloning", "Waardering geven, sociale erkenning")
    },
    (3.0, 3.9): {
        "proces": ("Grotendeels geborgd", "Nog risico bij drukte", "Blijvende reminders, standaardisering"),
        "technologie": ("Consistent gebruik bij meerderheid", "Enkele afhakers", "Verhalen delen, nudging via peers"),
        "structuur": ("Rol en structuur meestal geborgd", "Afhankelijk van teamlead", "Verantwoordelijkheid in team zichtbaar maken"),
        "cultuur": ("Nieuwe normen worden gevolgd", "Nog onzeker in informele sfeer", "Erken gedrag, continue reflectie")
    },
    (4.0, 5.0): {
        "proces": ("Verandering is standaardpraktijk", "Proces zit in het systeem", "Blijf belonen, deel good practices"),
        "technologie": ("Toolgebruik vanzelfsprekend", "Volledige integratie", "Ambassadeurschap onderhouden"),
        "structuur": ("Nieuwe structuur is de norm", "Teams functioneren soepel", "Gebruik voor nieuwe transities als referentie"),
        "cultuur": ("Nieuwe cultuur gedragen door iedereen", "Gedrag is onbewust congruent", "Koester cultuurdragers, onboarding verankeren")
    }
}
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
