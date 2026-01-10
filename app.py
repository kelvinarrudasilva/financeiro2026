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
# ESTILO
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
# FRASE DIÁRIA
# =========================
FRASES = [
    "Disciplina hoje, liberdade amanhã.",
    "Dinheiro gosta de silêncio e constância.",
    "Pouco a pouco, muito."
]

QUOTE_FILE = "quote.txt"

def frase_dia():
    hoje = date.today().isoformat()
    if os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            d = f.readline().strip()
            t = f.readline().strip()
            if d == hoje:
                return t
    frase = random.choice(FRASES)
    with open(QUOTE_FILE, "w", encoding="utf-8") as f:
        f.write(f"{hoje}\n{frase}")
    return frase

st.title("🔑 Virada Financeira")
st.markdown(f"<div class='quote-card'>{frase_dia()}</div>", unsafe_allow_html=True)

# =========================
# PLANILHA
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

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
# ABAS
# =========================
tabs = st.tabs(["📊 Financeiro", "💼 Investimentos"])

# ======================================================
# ABA FINANCEIRO (SEU APP ORIGINAL)
# ======================================================
with tabs[0]:
    try:
        df = pd.read_excel(PLANILHA_URL)
    except:
        st.error("Erro ao carregar planilha.")
        st.stop()

    receitas = df.iloc[1:, 1:5].copy()
    receitas.columns = ["DATA","MES","DESCRICAO","VALOR"]
    despesas = df.iloc[1:, 6:10].copy()
    despesas.columns = ["DATA","MES","DESCRICAO","VALOR"]

    for base in [receitas, despesas]:
        base["VALOR"] = base["VALOR"].apply(limpar_valor)
        base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
        base.dropna(subset=["DATA"], inplace=True)
        base["ANO"] = base["DATA"].dt.year
        base["MES_NUM"] = base["DATA"].dt.month
        base["MES"] = base["DATA"].dt.strftime("%b").str.lower()

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
    c2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
    c3.metric("⚖️ Saldo Geral", formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum()))

# ======================================================
# ABA INVESTIMENTOS
# ======================================================
with tabs[1]:
    st.subheader("💼 Investimentos — Meta R$ 40.000")

    try:
        inv = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO")
    except:
        st.error("Aba INVESTIMENTO não encontrada.")
        st.stop()

    inv = inv.iloc[:, 0:3].copy()
    inv.columns = ["DATA", "DESCRICAO", "VALOR"]

    inv["DATA"] = pd.to_datetime(inv["DATA"], errors="coerce")
    inv["VALOR"] = inv["VALOR"].apply(limpar_valor)
    inv.dropna(subset=["DATA"], inplace=True)

    inv = inv.sort_values("DATA")
    inv["ACUMULADO"] = inv["VALOR"].cumsum()

    total = inv["ACUMULADO"].iloc[-1] if not inv.empty else 0
    meta = 40000
    falta = meta - total

    c1, c2 = st.columns(2)
    c1.metric("💰 Total guardado", formato_real(total))
    c2.metric("🎯 Falta para 40k", formato_real(max(falta, 0)))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=inv["DATA"],
        y=inv["ACUMULADO"],
        mode="lines+markers",
        line=dict(width=3),
        name="Acumulado"
    ))

    fig.add_hline(
        y=meta,
        line_dash="dash",
        annotation_text="META 40K",
        annotation_position="top left"
    )

    fig.update_layout(
        height=420,
        xaxis_title="Tempo",
        yaxis_title="Valor (R$)",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
