import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
import requests
import random
import os

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="💰 Virada Financeira",
    page_icon="🔑",
    layout="wide"
)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
html, body, [data-testid="stApp"] { background-color: #0e0e11; }
.block-container { max-width: 1200px; }
.quote-card {
    background: #16161d;
    padding: 18px;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
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
    "O sucesso vem para quem não desiste.",
    "Disciplina hoje, liberdade amanhã.",
    "Pequenos passos constroem grandes resultados."
]

QUOTE_FILE = "quote.txt"

def load_quote():
    hoje = date.today().isoformat()
    if os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            saved = f.readline().strip()
            frase = f.readline().strip()
        if saved == hoje:
            return frase
    frase = random.choice(FRASES)
    with open(QUOTE_FILE, "w", encoding="utf-8") as f:
        f.write(f"{hoje}\n{frase}")
    return frase

st.title("🔑 Virada Financeira")
st.markdown(f'<div class="quote-card">{load_quote()}</div>', unsafe_allow_html=True)

# =========================
# PLANILHA GOOGLE
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
    if pd.isna(v):
        return 0.0
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(v)
        except:
            return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# LEITURA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except:
    st.error("❌ Não foi possível carregar a planilha.")
    st.stop()

# =========================
# VALIDAÇÃO (9 COLUNAS)
# =========================
if df.shape[1] < 9:
    st.error(f"A planilha retornou apenas {df.shape[1]} colunas.")
    st.write(df.head())
    st.stop()

# RECEITAS (colunas 1-4)
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA","MES","DESCRICAO","VALOR"]

# DESPESAS (colunas 5-8)
despesas = df.iloc[1:, 5:9].copy()
despesas.columns = ["DATA","MES","DESCRICAO","VALOR"]

# =========================
# TRATAMENTO
# =========================
for base in [receitas, despesas]:
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.upper()

# =========================
# MÉTRICAS
# =========================
st.subheader("📌 Visão Geral")

total_rec = receitas["VALOR"].sum()
total_des = despesas["VALOR"].sum()
saldo = total_rec - total_des

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Total", formato_real(total_rec))
c2.metric("💸 Despesa Total", formato_real(total_des))
c3.metric("⚖️ Saldo Geral", formato_real(saldo))

st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["MES_ANO"] = resumo["MES"] + "/" + resumo["ANO"].astype(str)

# =========================
# GRÁFICO
# =========================
st.subheader("📊 Balanço Financeiro")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["RECEITA"],
    name="Receita"
))

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["DESPESA"],
    name="Despesa"
))

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["SALDO"],
    name="Saldo"
))

fig.update_layout(
    barmode='group',
    height=450
)

st.plotly_chart(fig, use_container_width=True)
