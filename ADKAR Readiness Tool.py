import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="ADKAR Readiness Profiel", layout="wide")
st.title("📊 ADKAR Readiness Profiel Tool")
st.markdown("**Powered by Milan Lentze – OCM ADKAR Design**")

st.markdown("""
Deze tool helpt je om de veranderbereidheid van een team of organisatie in kaart te brengen aan de hand van het ADKAR-model.
Vul de score in (1.0–5.0) voor elk domein:
""")

# Contextvelden
with st.expander("🧩 Contextinformatie toevoegen"):
    context = st.text_input("Welke verandering betreft het?")
    doelgroep = st.selectbox("Welke doelgroep betreft het?", ["Zorgmedewerkers", "Leidinggevenden", "IT", "Overig"])

# Invoerform
with st.form("adkar_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        awareness = st.slider("Awareness (waarom de verandering nodig is)", 1.0, 5.0, 3.0, 0.1)
        desire = st.slider("Desire (motivatie om te veranderen)", 1.0, 5.0, 3.0, 0.1)
    with col2:
        knowledge = st.slider("Knowledge (hoe te veranderen)", 1.0, 5.0, 3.0, 0.1)
        ability = st.slider("Ability (vaardigheid om het te doen)", 1.0, 5.0, 3.0, 0.1)
    with col3:
        reinforcement = st.slider("Reinforcement (bekrachtiging en borging)", 1.0, 5.0, 3.0, 0.1)

    session_name = st.text_input("Sessienaam of teamlabel", value=f"sessie_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    compare_upload = st.file_uploader("📁 Vergelijk met eerder opgeslagen sessie (optioneel)", type="json")
    submitted = st.form_submit_button("🔍 Analyseer")

if submitted:
    adkar_scores = {
        "Awareness": awareness,
        "Desire": desire,
        "Knowledge": knowledge,
        "Ability": ability,
        "Reinforcement": reinforcement
    }

    # Grafiek voorbereiden
    categories = list(adkar_scores.keys())
    values = list(adkar_scores.values()) + [list(adkar_scores.values())[0]]
    categories += categories[:1]

    fig = go.Figure(data=[go.Scatterpolar(r=values, theta=categories, fill='toself', name='Huidige Scan')])

    # Eventuele vergelijking toevoegen
    if compare_upload:
        compare_data = json.load(compare_upload)
        compare_scores = compare_data.get("scores", {})
        if compare_scores:
            compare_values = list(compare_scores.values()) + [list(compare_scores.values())[0]]
            fig.add_trace(go.Scatterpolar(r=compare_values, theta=categories, fill='none', name='Vergelijking'))

    fig.update_layout(title="ADKAR Radar Profiel", polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

    # Analyse per domein
    st.header("💡 Analyse en Aanbevelingen")
    for factor, score in adkar_scores.items():
        if score <= 2:
            st.warning(f"**{factor} ({score}/5):** Kritiek laag. Interventies aanbevolen.")
            st.markdown("- 👉 Organiseer gerichte sessies / communicatiecampagne")
            st.markdown("- 👉 Betrek key influencers / ambassadeurs")
        elif score <= 3.5:
            st.info(f"**{factor} ({score}/5):** Gemiddeld. Aandachtspunt.")
            st.markdown("- 🔍 Verdiep in specifieke drempels via dialoog of observatie")
        else:
            st.success(f"**{factor} ({score}/5):** Sterk. Hou dit vast en versterk waar nodig.")

    # Gemiddelde en roadmap
    average = sum(adkar_scores.values()) / 5
    st.subheader("🧭 Samenvattend advies")
    if average < 3:
        st.error("🚨 Lage veranderrijpheid. Meerdere domeinen vereisen actie.")
    elif average < 4:
        st.warning("⚠️ Redelijke basis. Verbeteracties aanbevolen in zwakkere domeinen.")
    else:
        st.success("✅ Goede veranderrijpheid. Versterk en borg bestaande kracht.")

    weakest = min(adkar_scores, key=adkar_scores.get)
    st.markdown(f"**➡️ Start je roadmap bij:** {weakest} — dit domein scoort het laagst.")

    # Roadmap visualisatie
    st.markdown("""
    ### 🔄 Aanbevolen Fasen:
    1. **Bewustwording vergroten** (Awareness)
    2. **Motivatie stimuleren** (Desire)
    3. **Kennisontwikkeling organiseren** (Knowledge)
    4. **Oefen- en begeleidingsruimte creëren** (Ability)
    5. **Verankeren in gedrag, beleid en systemen** (Reinforcement)
    """)

    # Downloadbare sessie
    export_data = {
        "sessie": session_name,
        "timestamp": datetime.now().isoformat(),
        "scores": adkar_scores,
        "context": context,
        "doelgroep": doelgroep
    }
    json_str = json.dumps(export_data, indent=2)
    st.download_button("💾 Download sessie (.json)", data=json_str, file_name=f"{session_name}.json", mime="application/json")
