# Verbeterde ADKAR Scan Tool met visuele UI upgrades

import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import json
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="ADKAR Scan Tool", layout="wide")

# === Constantes ===
ADKAR_DOMAINS = ["Awareness", "Desire", "Knowledge", "Ability", "Reinforcement"]
CHANGE_TYPES = ["proces", "technologie", "structuur", "cultuur"]
DOMAIN_COLORS = {
    "Awareness": "#FFA07A",
    "Desire": "#F4A460",
    "Knowledge": "#87CEFA",
    "Ability": "#90EE90",
    "Reinforcement": "#DDA0DD"
}

# === Laad matrix (voor demo hier leeg gelaten – vul aan zoals eerder) ===
FEEDBACK_MATRIX = {...}  # Gebruik je bestaande matrix hier

st.title("📘 ADKAR Readiness Scan")
st.markdown("Beoordeel elk ADKAR-domein en ontvang gedragssignalen, oorzaken en aanbevelingen.")

results = {}

# === Invoer per domein ===
for domain in ADKAR_DOMAINS:
    with st.expander(f"📍 {domain}"):
        score = st.slider(f"Score voor {domain}", 1.0, 5.0, step=0.1)
        change_type = st.selectbox(f"Type verandering voor {domain}", CHANGE_TYPES, key=domain)

        feedback = ("", "", "")
        if domain in FEEDBACK_MATRIX:
            for (low, high), types in FEEDBACK_MATRIX[domain].items():
                if low <= score <= high:
                    feedback = types.get(change_type, ("", "", ""))
                    break

        st.markdown(f"🧠 **Gedragssignaal:** _{feedback[0]}_")
        st.markdown(f"📉 **Mogelijke oorzaak:** _{feedback[1]}_")
        st.markdown(f"🛠️ **Aanpak/interventie:** _{feedback[2]}_")

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

# === Bar Chart (Matplotlib) ===
st.subheader("📈 Score per Domein")
fig_bar, ax = plt.subplots(figsize=(8, 4))
bar_labels = ADKAR_DOMAINS
bar_scores = [results[d]["score"] for d in bar_labels]
colors = [DOMAIN_COLORS[d] for d in bar_labels]
ax.bar(bar_labels, bar_scores, color=colors)
ax.set_ylim(0, 5)
ax.set_ylabel("Score")
ax.set_title("ADKAR Domeinscores")
st.pyplot(fig_bar)

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


        )
