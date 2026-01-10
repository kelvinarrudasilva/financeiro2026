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
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1300px; }
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
[data-testid="metric-label"] { color: var(--muted); }
[data-testid="metric-value"] { font-size: 1.6rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# =========================
# PLANILHA GOOGLE DRIVE
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

# =========================
# FUNÇÕES AUXILIARES
# =========================
def limpar_valor(v):
    if pd.isna(v):
        return 0.0
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(v)
        except:
            return 0.0
    return float(v)

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# LEITURA DA PLANILHA
# =========================
try:
    df_principal = pd.read_excel(PLANILHA_URL)
    df_invest = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO")
except:
    st.error("❌ Erro ao carregar a planilha ou a aba INVESTIMENTO.")
    st.stop()

# =========================
# BASE RECEITAS / DESPESAS
# =========================
receitas = df_principal.iloc[1:, 1:5].copy()
receitas.columns = ["DATA","MES","DESCRICAO","VALOR"]

despesas = df_principal.iloc[1:, 6:10].copy()
despesas.columns = ["DATA","MES","DESCRICAO","VALOR"]

for base in [receitas, despesas]:
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base.dropna(subset=["DATA"], inplace=True)

# =========================
# INVESTIMENTOS
# =========================
df_invest["VALOR"] = df_invest["VALOR"].apply(limpar_valor)
dinheiro_guardado = df_invest["VALOR"].sum()

# =========================
# VISÃO GERAL
# =========================
st.subheader("📌 Visão Geral")

c1, c2, c3, c4 = st.columns(4)

c1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
c2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
c3.metric("⚖️ Saldo Geral", formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum()))
c4.metric("💰 Dinheiro guardado", formato_real(dinheiro_guardado))
