import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="ADKAR Readiness Profiel", layout="wide")
st.title("📊 ADKAR Readiness Profiel Tool")
st.markdown("**Powered by Milan Lentze – AI Change Design**")

st.markdown("""
Deze tool helpt je om de veranderbereidheid van een team of organisatie in kaart te brengen aan de hand van het ADKAR-model.
Vul de score in (1–5) voor elk domein:
""")

# Input sliders
with st.form("adkar_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        awareness = st.slider("Awareness (inzicht in het waarom)", 1, 5, 3)
        desire = st.slider("Desire (motivatie om te veranderen)", 1, 5, 3)
    with col2:
        knowledge = st.slider("Knowledge (kennis van hoe te veranderen)", 1, 5, 3)
        ability = st.slider("Ability (vaardigheid om het te doen)", 1, 5, 3)
    with col3:
        reinforcement = st.slider("Reinforcement (bekrachtiging / verankering)", 1, 5, 3)

    submitted = st.form_submit_button("🔍 Analyseer")

if submitted:
    adkar_scores = {
        "Awareness": awareness,
        "Desire": desire,
        "Knowledge": knowledge,
        "Ability": ability,
        "Reinforcement": reinforcement
    }

    # Visualisatie: radar chart
    categories = list(adkar_scores.keys())
    values = list(adkar_scores.values())
    values += values[:1]
    categories += categories[:1]

    fig = go.Figure(
        data=[go.Scatterpolar(r=values, theta=categories, fill='toself', name='ADKAR Profiel')],
        layout=go.Layout(
            title=go.layout.Title(text='ADKAR Radar Profiel'),
            polar={'radialaxis': {'visible': True, 'range': [0, 5]}},
            showlegend=False
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Uitleg en aanbevelingen
    st.header("💡 Analyse en Aanbevelingen")

    for factor, score in adkar_scores.items():
        if score <= 2:
            st.warning(f"**{factor} is laag ({score}/5):** Dit vormt een risico voor succesvolle verandering.")
        elif score == 3:
            st.info(f"**{factor} is gemiddeld (3/5):** Aandachtspunt om te versterken.")
        else:
            st.success(f"**{factor} is sterk ({score}/5):** Geen directe actie vereist.")

    # Eindoordeel
    average = sum(adkar_scores.values()) / 5
    if average < 3:
        st.error("🚨 Algemeen beeld: Lage veranderrijpheid. Er zijn meerdere kritieke zwakke punten.")
    elif average < 4:
        st.warning("⚠️ Algemeen beeld: Redelijke basis, maar er is versterking nodig op meerdere fronten.")
    else:
        st.success("✅ Algemeen beeld: Sterke veranderrijpheid. Houd momentum vast en blijf monitoren.")
