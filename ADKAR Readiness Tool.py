import streamlit as st
import pandas as pd
import json
import datetime
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="ADKAR Readiness 2.0", layout="wide")

st.title("🧭 ADKAR Readiness Profiler 2.0")
st.markdown("Een diepgaande scan voor verandermanagement")

# --- Session meta info ---
st.sidebar.header("📋 Sessiedetails")
session_name = st.sidebar.text_input("Naam sessie", value="Sessie " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
doelgroep = st.sidebar.text_input("Doelgroep (bv. team, afdeling)")
change_type = st.sidebar.selectbox("Type verandering", ["Proces", "Technologie", "Structuur", "Cultuur", "Anders"])

# --- Sliders ---
st.sidebar.markdown("---")
st.sidebar.header("🎯 ADKAR Scores")
awareness = st.sidebar.slider("Awareness", 1.0, 5.0, 3.0, 0.1)
desire = st.sidebar.slider("Desire", 1.0, 5.0, 3.0, 0.1)
knowledge = st.sidebar.slider("Knowledge", 1.0, 5.0, 3.0, 0.1)
ability = st.sidebar.slider("Ability", 1.0, 5.0, 3.0, 0.1)
reinforcement = st.sidebar.slider("Reinforcement", 1.0, 5.0, 3.0, 0.1)

scores = {
    "Awareness": awareness,
    "Desire": desire,
    "Knowledge": knowledge,
    "Ability": ability,
    "Reinforcement": reinforcement
}

# --- Analysis logic ---
def interpret_score(domain, score):
    levels = {
        "Awareness": [
            (1.9, "Volledige onwetendheid of verwarring", "Geen communicatie, vaagheid, overload", "Visuele storytelling, urgentiecampagnes, leiderschapscascade"),
            (2.9, "Weinig tot oppervlakkig begrip", "Te algemene uitleg, misconnectie met werkpraktijk", "Context-specifieke voorbeelden, vertaalsessies op teamniveau"),
            (3.9, "Begrip aanwezig maar niet overtuigend", "Info ontvangen maar geen verbinding", "Dialoogsessies, framingworkshops, ‘wat betekent dit voor mij?’"),
            (5.0, "Helder en geaccepteerd waarom het nodig is", "Transparante communicatie, heldere richting", "Storytelling delen, versterken via informele netwerken")
        ],
        "Desire": [
            (1.9, "Actieve weerstand of passieve sabotering", "Angst, statusverlies, overload", "Luistersessies, invloed geven, dialoog op waarden"),
            (2.9, "Afstandelijk of sceptisch", "Verlies van autonomie, geen vertrouwen", "Peer influence, inspirerende koplopers, persoonlijke benefits zichtbaar maken"),
            (3.9, "Neutrale houding, afwachtend", "Zien wel het nut, maar nog geen energie", "Change ambassadors inzetten, betrokkenheid via co-creatie"),
            (5.0, "Positieve energie, enthousiasme", "Begrip + persoonlijk belang herkend", "Versterken, podium geven aan enthousiaste collega’s")
        ],
        "Knowledge": [
            (1.9, "Geen idee wat ik moet doen", "Geen training, te abstract, overload", "Praktijkgerichte instructie, video’s, demo’s"),
            (2.9, "Er is training, maar verwarring blijft", "Generieke content, geen vertaalslag", "Rollen-specifieke uitleg, buddy system"),
            (3.9, "Begrip, maar onzeker over details", "Teveel tegelijk, vergeten na training", "Refreshers, just-in-time support, Q&A"),
            (5.0, "Duidelijk wat wanneer verwacht wordt", "Heldere tools, structuur, herhaling", "Borg in onboarding, laat experts begeleiden")
        ],
        "Ability": [
            (1.9, "Onzekerheid, fouten, frustratie", "Geen tijd, geen oefenruimte, systeemhindernissen", "Safe practice-omgeving, mentorhulp, druk verminderen"),
            (2.9, "Pogingen, maar weerstand door complexiteit", "Technische of procedurele barrières", "Simpel maken, stapsgewijze implementatie"),
            (3.9, "Het lukt deels, met onzekerheid", "Ervaring groeit, maar afhankelijk van hulp", "Ondersteuning uitbreiden, feedbackloops creëren"),
            (5.0, "Volwaardig kunnen uitvoeren", "Ruimte, middelen, ervaring aanwezig", "Laat collega's anderen trainen (train-de-trainer)")
        ],
        "Reinforcement": [
            (1.9, "Oude gedrag keert terug, niemand zegt iets", "Geen opvolging, leiderschap negeert verandering", "Evaluaties, consequenties, leiders betrekken"),
            (2.9, "Enkele pogingen, niet structureel", "Geen beleid, geen zichtbaar voorbeeldgedrag", "Successen vieren, beleid integreren"),
            (3.9, "Soms zichtbaar, afhankelijk van team", "Geen uniforme aanpak, leiderschap niet consistent", "Belonen gewenst gedrag, gedrag meetbaar maken"),
            (5.0, "Verandering is onderdeel van cultuur", "Structuren zijn aangepast, gedrag is norm", "Continu feedback, cultuurdragers versterken")
        ]
    }
    for threshold, signal, cause, advice in levels[domain]:
        if score <= threshold:
            return signal, cause, advice

# --- Visual ---
fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=list(scores.values()),
    theta=list(scores.keys()),
    fill='toself',
    name='Huidige score',
    line=dict(color='royalblue')
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False, height=450)
st.plotly_chart(fig, use_container_width=True)

# --- Analyse ---
st.subheader("🔎 Analyse per domein")
for domein, score in scores.items():
    gedrag, oorzaak, interventie = interpret_score(domein, score)
    st.markdown(f"**{domein} ({score:.1f})**")
    st.markdown(f"- **Gedragssignaal:** {gedrag}")
    st.markdown(f"- **Oorzaak:** {oorzaak}")
    st.markdown(f"- **Aanpak:** {interventie}")
    st.markdown("---")

# --- Roadmap ---
st.subheader("📍 Focusadvies")
min_domein = min(scores, key=scores.get)
st.info(f"Start met het domein **{min_domein}**, dat met een score van {scores[min_domein]:.1f} de meeste aandacht vereist.")

# --- Export ---
if st.button("💾 Download resultaten (.json)"):
    result = {
        "session_name": session_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "doelgroep": doelgroep,
        "change_type": change_type,
        "scores": scores
    }
    st.download_button(
        label="Download JSON",
        file_name=f"{session_name.replace(' ', '_')}.json",
        mime="application/json",
        data=json.dumps(result, indent=2)
    )
