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
h1 { font-weight: 700; }
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
[data-testid="metric-label"] { color: var(--muted); font-size: 0.85rem; }
[data-testid="metric-value"] { font-size: 1.6rem; font-weight: 700; }
.quote-card {
    background: linear-gradient(145deg, #1b1b24, #16161d);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #1f1f2b;
    margin-bottom: 1.5rem;
    font-size: 1.4rem;
    color: #9ca3af;
    font-style: italic;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FRASE DIÁRIA
# =========================
FRASES_FALLBACK = [
    "Disciplina hoje, liberdade amanhã.",
    "O dinheiro obedece quem pensa antes de gastar.",
    "Quem governa o mês, governa o ano.",
]

def get_quote():
    try:
        r = requests.get("https://motivacional.top/api.php?acao=aleatoria", timeout=3)
        return r.json()["dados"][0]["frase"]
    except:
        return random.choice(FRASES_FALLBACK)

st.title("🔑 Virada Financeira")
st.markdown(f'<div class="quote-card">{get_quote()}</div>', unsafe_allow_html=True)

# =========================
# PLANILHA
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH/export?format=xlsx"
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
# LEITURA
# =========================
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

# =========================
# SELECTOR — MÊS ATUAL + PRÓXIMO
# =========================
hoje = datetime.now()
mes_atual = hoje.strftime("%b").lower()
ano_atual = hoje.year

if hoje.month == 12:
    prox_mes = "jan"
    prox_ano = ano_atual + 1
else:
    prox_mes = datetime(ano_atual, hoje.month + 1, 1).strftime("%b").lower()
    prox_ano = ano_atual

opcoes = [
    f"{mes_atual}/{ano_atual}",
    f"{prox_mes}/{prox_ano}"
]

opcoes = [o.upper() for o in opcoes]

mes_sel = st.selectbox("📅 Escolha o mês", opcoes, index=0)
mes_txt, ano_sel = mes_sel.lower().split("/")
ano_sel = int(ano_sel)

# =========================
# DETALHAMENTO — AGORA NO TOPO
# =========================
st.subheader(f"📆 Detalhamento — {mes_sel}")

rec_mes = receitas[(receitas["ANO"]==ano_sel)&(receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel)&(despesas["MES"]==mes_txt)]

c1, c2, c3 = st.columns(3)
c1.metric("💰 Receitas", formato_real(rec_mes["VALOR"].sum()))
c2.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
c3.metric("⚖️ Saldo", formato_real(rec_mes["VALOR"].sum()-des_mes["VALOR"].sum()))

# =========================
# COMPOSIÇÃO DO MÊS
# =========================
st.subheader("📌 Composição do mês")
col_r, col_d = st.columns(2)

with col_r:
    if not rec_mes.empty:
        fig_r = px.pie(
            rec_mes, values="VALOR", names="DESCRICAO", hole=0.55, title="Receitas"
        )
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Nenhuma receita registrada.")

with col_d:
    if not des_mes.empty:
        top = des_mes.sort_values("VALOR", ascending=False).head(10)
        fig_d = px.bar(
            top, x="VALOR", y="DESCRICAO", orientation="h", title="Top despesas"
        )
        st.plotly_chart(fig_d, use_container_width=True)
    else:
        st.info("Nenhuma despesa registrada.")

# =========================
# RESUMO GERAL
# =========================
st.divider()
st.subheader("📌 Visão Geral")

v1, v2, v3 = st.columns(3)
v1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
v2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
v3.metric("⚖️ Saldo Geral", formato_real(receitas["VALOR"].sum()-despesas["VALOR"].sum()))

# =========================
# BALANÇO FINANCEIRO (AGORA EMBAIXO)
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum()
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum()

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo.columns = ["ANO","MES_NUM","MES","RECEITA","DESPESA"]
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo["MES_ANO"] = resumo["MES"].str.upper() + "/" + resumo["ANO"].astype(str)

st.subheader("📊 Balanço Financeiro")
fig = go.Figure()

fig.add_bar(x=resumo["MES_ANO"], y=resumo["RECEITA"], name="Receita")
fig.add_bar(x=resumo["MES_ANO"], y=resumo["DESPESA"], name="Despesa")
fig.add_bar(x=resumo["MES_ANO"], y=resumo["SALDO"], name="Saldo")

fig.update_layout(barmode="group", height=450)
st.plotly_chart(fig, use_container_width=True)
