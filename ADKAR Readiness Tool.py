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
    .streamlit-expanderHeader {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #333;
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


st.title("📘 ADKAR Analyse")
st.markdown("MDLentze")
st.markdown(" ")
st.markdown("Beoordeel elk ADKAR-domein en verkrijg inzichten in mogelijke gedragssignalen, oorzaken en aanbevelingen.")

results = {}

# === Keuze van type verandering ===
change_type = st.selectbox("Selecteer het type verandering:", CHANGE_TYPES)

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
        <h5 style="margin-bottom: 0.8rem;">{status_label}</h5>
        <p style="margin-bottom: 0.4rem;"><strong>Type verandering:</strong> {change_type.capitalize()}</p>
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
# === Witruimte boven de titel
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")

# === ADKAR Profieloverzicht Blok ===

with st.container():
    st.markdown('<div class="gray-box-content">', unsafe_allow_html=True)

    st.markdown("### 📊 ADKAR Profieloverzicht")

    st.markdown(" ")
    st.markdown(" ")

    # Bereken gemiddelde
    avg_score = round(np.mean([v["score"] for v in results.values()]), 2)

    # === 1. Gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_score,
        title={'text': "Gemiddelde ADKAR-score"},
        gauge={
            'axis': {'range': [1, 5], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "royalblue"},
            'steps': [
                {'range': [1.0, 2.0], 'color': '#ffcccc'},
                {'range': [2.0, 3.0], 'color': '#ffe0b3'},
                {'range': [3.0, 4.0], 'color': '#ffffb3'},
                {'range': [4.0, 5.0], 'color': '#ccffcc'}
            ],
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))

    # === 2. Radar chart
    labels = ADKAR_DOMAINS.copy()
    scores = [results[d]["score"] for d in labels]
    scores += scores[:1]
    labels += labels[:1]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=scores,
        theta=labels,
        fill='toself',
        name='ADKAR Scores',
        line=dict(color='royalblue')
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False,
        height=250,
        margin=dict(l=10, r=10, t=10, b=10)
    )
     
# === 3. Samenvatting Matrix
    summary_matrix = {
            "Proces": {
                (1.0, 2.0): "🔴 De organisatie ervaart actieve of passieve weerstand tegen de nieuwe processen. Medewerkers houden vast aan oude werkwijzen en tonen weinig tot geen bereidheid om zich aan te passen. Dit vormt een directe bedreiging voor succesvolle implementatie en vereist intensieve interventie.",
                (2.0, 3.0): "🟠 Er is sprake van beperkte acceptatie. Medewerkers zijn afwachtend en begrijpen het nut van de verandering niet volledig. De nieuwe processen worden mogelijk wel toegepast, maar zonder overtuiging of consistentie. Er is risico op terugval of schijnacceptatie.",
                (3.0, 4.0): "🟡 De organisatie past de nieuwe processen grotendeels toe, maar nog niet vanzelfsprekend of efficiënt. Er is ruimte voor verbetering in vaardigheid, vertrouwen of motivatie. Zonder aanvullende ondersteuning blijft de verandering kwetsbaar of versnipperd.",
                (4.0, 5.0): "🟢 De verandering wordt in de meeste delen van de organisatie goed toegepast. Medewerkers zien de meerwaarde en handelen ernaar. Wel is continue versterking nodig om terugval te voorkomen en het gedrag structureel te verankeren.",
                (5.0,):     "🟢 De procesverandering is volledig geïntegreerd in het dagelijks werk. Medewerkers tonen eigenaarschap, passen de processen proactief toe en verbeteren ze zelfs waar mogelijk. De organisatie functioneert aantoonbaar beter op basis van de nieuwe werkwijzen."
            },
            "Technologie": {
                (1.0, 2.0): "🔴 De organisatie kampt met weerstand tegen het nieuwe systeem of tool. Medewerkers vermijden gebruik, tonen frustratie en ervaren onzekerheid of angst. De verandering ondermijnt productiviteit en levert risico’s op voor fouten of inefficiëntie.",
                (2.0, 3.0): "🟠 De technologie wordt met moeite toegepast. Medewerkers gebruiken de tool alleen wanneer het moet, vaak met fouten of inefficiëntie. Er is een duidelijke kloof in vaardigheden en vertrouwen, waardoor draagvlak ontbreekt.",
                (3.0, 4.0): "🟡 Het systeem wordt grotendeels gebruikt, maar niet optimaal. Medewerkers kennen de basis, maar benutten de technologie niet efficiënt. Er is risico op suboptimaal gebruik en frustratie bij complexere taken.",
                (4.0, 5.0): "🟢 De technologie wordt functioneel en met vertrouwen gebruikt. Medewerkers zien het voordeel, werken er dagelijks mee en helpen collega’s. Borging en optimalisatie zijn nodig om het gebruik structureel en toekomstbestendig te maken.",
                (5.0,):     "🟢 De technologie is vanzelfsprekend onderdeel van het werk. Medewerkers benutten het systeem effectief, denken mee over verbetering en dragen actief bij aan innovatie of opschaling."
            },
            "Structuur": {
                (1.0, 2.0): "🔴 De organisatie ervaart chaos of weerstand. Medewerkers begrijpen hun nieuwe rol niet of verzetten zich tegen verlies van status, teamverband of duidelijkheid. Dit leidt tot verminderde samenwerking en risico op interne frictie.",
                (2.0, 3.0): "🟠 De structuur is formeel aangepast, maar wordt nog niet begrepen of gedragen. Er is verwarring over verantwoordelijkheden, besluitvorming en positionering. Dit belemmert de effectiviteit van teams en leiderschap.",
                (3.0, 4.0): "🟡 Er is een begin van structuuracceptatie, maar inconsistentie in toepassing en gedrag. Sommige teams functioneren volgens de nieuwe lijnen, anderen vallen terug in oude patronen. Er is behoefte aan heldere rolduiding en alignment.",
                (4.0, 5.0): "🟢 De nieuwe structuur wordt grotendeels gevolgd en medewerkers nemen hun rol serieus. Wel zijn er nog vragen of onduidelijkheden bij cross-functionele samenwerking of escalatiepunten. Stabilisatie is nodig.",
                (5.0,):     "🟢 De structuur is volledig geïntegreerd. Rollen, mandaten en samenwerking zijn helder en efficiënt. De organisatie is wendbaar en medewerkers opereren met vertrouwen binnen hun nieuwe context."
            },
            "Cultuur": {
                (1.0, 2.0): "🔴 De cultuurverandering wordt verworpen of genegeerd. Medewerkers geloven niet in de gewenste waarden of zien deze als onrealistisch of top-down opgelegd. Informele normen ondermijnen de gewenste gedragsverandering.",
                (2.0, 3.0): "🟠 De nieuwe cultuur wordt met scepsis bekeken. Medewerkers volgen formeel het gewenste gedrag, maar geloven er niet in. Oud gedrag wordt in stand gehouden via informele patronen of voorbeeldgedrag van leiders.",
                (3.0, 4.0): "🟡 De organisatie spreekt de nieuwe waarden uit, maar in gedrag is de verandering nog niet consistent zichtbaar. Er is bereidheid, maar ook onzekerheid over wat het concreet betekent. Cultuurverandering blijft oppervlakkig.",
                (4.0, 5.0): "🟢 De nieuwe cultuur wordt zichtbaar in gedrag en houding. Medewerkers herkennen de kernwaarden en passen die toe in samenwerking. Wel is voortdurende versterking en voorbeeldgedrag van leiders nodig.",
                (5.0,):     "🟢 De gewenste cultuur is vanzelfsprekend geworden. Waarden zijn voelbaar in taal, gedrag en besluitvorming. Medewerkers houden elkaar verantwoordelijk en zijn trots op de gedeelde identiteit van de organisatie."
            }
        }

    # Hulp: juiste tekst ophalen
    def get_summary(avg_score, change_type):
        for key in summary_matrix[change_type]:
            if len(key) == 1 and avg_score == key[0]:
                return summary_matrix[change_type][key]
            elif len(key) == 2:
                low, high = key
                if low <= avg_score < high:
                    return summary_matrix[change_type][key]
        return "⚠️ Geen samenvatting beschikbaar."

    summary_text = get_summary(avg_score, change_type)
    
    # --- Intervention Matrix
    intervention_matrix = {
        "Proces": {
            (1.0, 2.0): " Organiseer verdiepende sessies over het 'waarom' van de verandering. Zet interne ambassadeurs in en betrek teams actief bij het herontwerpen van hun werkproces.",
            (2.0, 3.0): " Gebruik storytelling en praktijkvoorbeelden om urgentie tastbaar te maken. Laat leidinggevenden het goede voorbeeld geven en bied ruimte voor dialoog.",
            (3.0, 4.0): " Bied extra coaching aan op gedragsniveau. Evalueer samen met teams waar knelpunten zitten en maak het nieuwe proces visueel en meetbaar.",
            (4.0, 5.0): " Versterk met peer feedback, vier successen, en koppel procesprestaties aan teamdoelstellingen. Houd het leerproces levend.",
            (5.0,):     " Geef eigenaarschap aan teams om processen te optimaliseren. Laat hen goede voorbeelden delen en stel hen in staat als interne adviseurs op te treden."
        },
        "Technologie": {
            (1.0, 2.0): " Start met kleinschalige pilots waarin medewerkers in een veilige omgeving kunnen oefenen. Laat tech-savvy collega’s optreden als buddy of coach.",
            (2.0, 3.0): " Bouw laagdrempelige handleidingen, video tutorials en quick reference cards. Faciliteer workshops waarin medewerkers hun zorgen kunnen uiten.",
            (3.0, 4.0): " Focus op praktijkgerichte training. Stimuleer dagelijkse toepassing door micro-learnings en dagelijkse ‘how-to’ momenten.",
            (4.0, 5.0): " Laat power users collega’s trainen. Verzamel en verspreid best practices en koppel feedback aan optimalisaties van de tool.",
            (5.0,):     " Monitor gebruik en impact met dashboards. Laat gebruikers meedenken over doorontwikkeling en beloon innovatief gebruik."
        },
        "Structuur": {
            (1.0, 2.0): " Organiseer heroriëntaties op rollen en mandaten. Creëer ruimte voor emoties bij verlies van status of verandering van hiërarchie.",
            (2.0, 3.0): " Maak verantwoordelijkheden visueel en expliciet (bv. via RACI-schema's). Laat teams gezamenlijk hun samenwerking herontwerpen.",
            (3.0, 4.0): " Verhelder escalatieroutes, beslisbevoegdheden en overlegstructuren. Laat leidinggevenden consistent sturen op nieuwe structuur.",
            (4.0, 5.0): " Koppel teamdoelen en resultaten aan de nieuwe structuur. Gebruik intervisie om structurele frictie op te lossen.",
            (5.0,):     " Monitor en optimaliseer continu de effectiviteit van de structuur. Betrek teams bij het herinrichten op basis van ervaringen."
        },
        "Cultuur": {
            (1.0, 2.0): " Start met dialoogsessies over de gewenste en huidige cultuur. Benoem onbespreekbaar gedrag en zet een ‘coalition of the willing’ op.",
            (2.0, 3.0): " Werk aan congruentie tussen formeel gedrag en informele signalen. Stimuleer kwetsbaar leiderschap en voorbeeldgedrag.",
            (3.0, 4.0): " Maak gewenste waarden concreet in gedrag. Gebruik storytelling, werkvormen en feedbackcycli om te oefenen met nieuw gedrag.",
            (4.0, 5.0): " Bouw voort op zichtbaar gedrag met peer coaching en rituelen. Leg cultuurverandering vast in onboarding en leiderschap.",
            (5.0,):     " Zet cultuurdragers in als mentor. Monitor cultuur met pulse surveys en vier momenten die symbool staan voor de kernwaarden."
        }
    }

    # --- Interventie op basis van score + type
    def get_intervention(avg_score, change_type):
        for key in intervention_matrix[change_type]:
            low = key[0]
            high = key[1] if len(key) > 1 else 5.0
            if low <= avg_score < high or avg_score == 5.0:
                return intervention_matrix[change_type][key]
        return "⚠️ Geen interventie gevonden."

    intervention_text = get_intervention(avg_score, change_type)
    
    # === 4. Lay-out visualisaties + samenvatting
    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.plotly_chart(fig_radar, use_container_width=True)

with right_col:
    st.markdown("#### ADKAR Samenvatting")
    
    st.markdown(f"""
    <div style='background-color: #f2f2f2; padding: 20px; border-radius: 10px;'>
        <p style='font-size: 18px; color: black;'>{summary_text}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown("#### Mogelijke eerste interventie stap")
    st.markdown(f"""
<div style='background-color: #f2f2f2; padding: 20px; border-radius: 10px;'>
        <p style='font-size: 18px; color: black;'>{intervention_text}</p>
    </div>
    """, unsafe_allow_html=True)
 
# === Witruimte boven de titel
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")
st.markdown(" ")

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
