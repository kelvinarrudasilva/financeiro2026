import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import requests
import random
import os
import numpy as np

# =========================
# CONFIGURAÇÃO GERAL
# =========================
st.set_page_config(
    page_title="💰 Virada Financeira",
    page_icon="🗝️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# ESTILO PREMIUM
# =========================
st.markdown("""
<style>
:root {
    --bg: #0e0e11;
    --card: #16161d;
    --muted: #9ca3af;
    --accent: #22c55e;
}
html, body, [data-testid="stApp"] { background-color: var(--bg); }
.block-container { max-width: 1300px; padding: 2rem; }
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
.quote-card {
    background: linear-gradient(145deg, #1b1b24, #16161d);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #1f1f2b;
    margin-bottom: 1.5rem;
    font-size: 1.3rem;
    color: #9ca3af;
    font-style: italic;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FRASE MOTIVADORA
# =========================
def get_quote():
    frases = [
        "Disciplina hoje, liberdade amanhã.",
        "O dinheiro gosta de quem tem plano.",
        "Constância vence talento financeiro.",
        "Devagar também é movimento."
    ]
    return random.choice(frases)

st.title("🔑 Virada Financeira")
st.markdown(f"<div class='quote-card'>{get_quote()}</div>", unsafe_allow_html=True)

# =========================
# PLANILHA
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

# =========================
# FUNÇÕES
# =========================
def limpar_valor(v):
    if pd.isna(v): return 0.0
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".")
    try:
        return float(v)
    except:
        return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# LEITURA BASE
# =========================
df = pd.read_excel(PLANILHA_URL)

# =========================
# INVESTIMENTOS
# =========================
investimentos = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO")
investimentos.columns = ["DATA", "VALOR"]
investimentos["DATA"] = pd.to_datetime(investimentos["DATA"], errors="coerce")
investimentos["VALOR"] = investimentos["VALOR"].apply(limpar_valor)
investimentos.dropna(subset=["DATA"], inplace=True)
investimentos = investimentos.sort_values("DATA")

investimentos["ANO"] = investimentos["DATA"].dt.year
investimentos["MES"] = investimentos["DATA"].dt.month

inv_mensal = investimentos.groupby(["ANO","MES"], as_index=False)["VALOR"].sum()
inv_mensal["DATA"] = pd.to_datetime(inv_mensal["ANO"].astype(str) + "-" + inv_mensal["MES"].astype(str) + "-01")
inv_mensal = inv_mensal.sort_values("DATA")
inv_mensal["ACUMULADO"] = inv_mensal["VALOR"].cumsum()

# =========================
# META
# =========================
META = 40000
saldo_atual = inv_mensal["ACUMULADO"].iloc[-1]
media_aporte = inv_mensal["VALOR"].mean()
taxa = 0.01

# =========================
# CONTADOR MESES
# =========================
saldo = saldo_atual
meses = 0
while saldo < META and meses < 240:
    saldo = (saldo + media_aporte) * (1 + taxa)
    meses += 1

# =========================
# MÉTRICAS
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("💼 Investido até hoje", formato_real(saldo_atual))
c2.metric("🎯 Meta", formato_real(META))
c3.metric("⏳ Faltam", f"{meses} meses")

st.divider()

# =========================
# PROJEÇÃO
# =========================
datas_proj = []
valores_proj = []
saldo = saldo_atual
data_base = inv_mensal["DATA"].iloc[-1]

for i in range(1, meses + 1):
    saldo = (saldo + media_aporte) * (1 + taxa)
    datas_proj.append(data_base + pd.DateOffset(months=i))
    valores_proj.append(saldo)

proj = pd.DataFrame({
    "DATA": datas_proj,
    "SALDO": valores_proj
})

# =========================
# GRÁFICO FINAL
# =========================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=inv_mensal["DATA"],
    y=inv_mensal["ACUMULADO"],
    mode="lines+markers",
    name="Real"
))

fig.add_trace(go.Scatter(
    x=proj["DATA"],
    y=proj["SALDO"],
    mode="lines+markers",
    name="Projeção 1% a.m.",
    line=dict(dash="dash")
))

fig.add_hline(
    y=META,
    line_dash="dot",
    line_color="gold",
    annotation_text="🎯 Meta 40k",
    annotation_position="top left"
)

fig.update_layout(
    height=450,
    xaxis_title="Tempo",
    yaxis_title="Patrimônio (R$)",
    margin=dict(l=20, r=20, t=40, b=20)
)

st.subheader("📈 Caminho até os R$ 40.000")
st.plotly_chart(fig, use_container_width=True)
