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
}
html, body, [data-testid="stApp"] { background-color: var(--bg); }
.block-container { max-width: 1300px; padding: 2rem; }
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CABEÇALHO
# =========================
st.title("🔑 Virada Financeira")

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
# ABAS
# =========================
tabs = st.tabs(["📊 Financeiro", "💎 Investimentos"])

# =====================================================================
# 📊 ABA FINANCEIRO (SEU CÓDIGO ORIGINAL — SEM ALTERAÇÃO FUNCIONAL)
# =====================================================================
with tabs[0]:
    df = pd.read_excel(PLANILHA_URL)

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

    st.subheader("📌 Visão Geral")
    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
    c2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
    c3.metric("⚖️ Saldo Geral", formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum()))

# =====================================================================
# 💎 ABA INVESTIMENTOS (INTELIGÊNCIA FINANCEIRA)
# =====================================================================
with tabs[1]:
    st.subheader("💎 Caminho até os R$ 40.000")

    investimentos = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO")
    investimentos.columns = ["DATA", "VALOR"]
    investimentos["DATA"] = pd.to_datetime(investimentos["DATA"])
    investimentos["VALOR"] = investimentos["VALOR"].apply(limpar_valor)
    investimentos = investimentos.sort_values("DATA")

    investimentos["ANO"] = investimentos["DATA"].dt.year
    investimentos["MES"] = investimentos["DATA"].dt.month

    inv_m = investimentos.groupby(["ANO","MES"], as_index=False)["VALOR"].sum()
    inv_m["DATA"] = pd.to_datetime(inv_m["ANO"].astype(str) + "-" + inv_m["MES"].astype(str) + "-01")
    inv_m = inv_m.sort_values("DATA")
    inv_m["ACUMULADO"] = inv_m["VALOR"].cumsum()

    # =========================
    # PARÂMETROS
    # =========================
    META = 40000
    MESES = 12
    JUROS = 0.01

    saldo_atual = inv_m["ACUMULADO"].iloc[-1]
    data_base = inv_m["DATA"].iloc[-1]

    # =========================
    # META COM JUROS
    # =========================
    falta = max(META - saldo_atual, 0)
    aporte_base = falta / MESES

    datas_meta, valores_meta = [], []
    saldo = saldo_atual

    for i in range(1, MESES + 1):
        saldo = (saldo + aporte_base) * (1 + JUROS)
        datas_meta.append(data_base + pd.DateOffset(months=i))
        valores_meta.append(saldo)

    meta_df = pd.DataFrame({"DATA": datas_meta, "META": valores_meta})

    # =========================
    # SIMULAÇÃO ATRASO 2 MESES
    # =========================
    datas_atraso, valores_atraso = [], []
    saldo = saldo_atual

    for i in range(1, MESES + 1):
        if i > 2:
            saldo = (saldo + aporte_base) * (1 + JUROS)
        else:
            saldo = saldo * (1 + JUROS)
        datas_atraso.append(data_base + pd.DateOffset(months=i))
        valores_atraso.append(saldo)

    atraso_df = pd.DataFrame({"DATA": datas_atraso, "ATRASO": valores_atraso})

    # =========================
    # INDICADOR VISUAL
    # =========================
    esperado_hoje = meta_df.iloc[0]["META"]
    status = "🟢 Acima da meta" if saldo_atual >= esperado_hoje else "🔴 Abaixo da meta"

    c1, c2, c3 = st.columns(3)
    c1.metric("💼 Atual", formato_real(saldo_atual))
    c2.metric("🎯 Meta final", formato_real(META))
    c3.metric("🚦 Status", status)

    # =========================
    # GRÁFICO FINAL
    # =========================
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=inv_m["DATA"],
        y=inv_m["ACUMULADO"],
        name="Real",
        mode="lines+markers",
        line=dict(width=3)
    ))

    fig.add_trace(go.Scatter(
        x=meta_df["DATA"],
        y=meta_df["META"],
        name="Meta com juros (1%)",
        mode="lines",
        line=dict(dash="dash", width=3)
    ))

    fig.add_trace(go.Scatter(
        x=atraso_df["DATA"],
        y=atraso_df["ATRASO"],
        name="Atraso 2 meses",
        mode="lines",
        line=dict(dash="dot", width=2)
    ))

    fig.add_hline(y=META, line_dash="dot", line_color="gold")

    fig.update_layout(
        height=450,
        xaxis_title="Tempo",
        yaxis_title="Patrimônio (R$)"
    )

    st.plotly_chart(fig, use_container_width=True)
