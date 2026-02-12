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
# ESTILO PREMIUM + FRASE
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
h1 { font-weight: 700; letter-spacing: 0.5px; }
h2, h3 { font-weight: 600; }
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
[data-testid="metric-label"] { color: var(--muted); font-size: 0.85rem; }
[data-testid="metric-value"] { font-size: 1.6rem; font-weight: 700; }
section[data-testid="stSidebar"] { background-color: #0b0b10; border-right: 1px solid #1f1f2b; }
hr { border: none; height: 1px; background: #1f1f2b; margin: 2rem 0; }
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
# FRASE MOTIVADORA
# =========================
FRASES_FALLBACK = [
    "Grandes conquistas exigem dedicação.",
    "O sucesso vem para quem não desiste.",
    "Disciplina constrói liberdade.",
    "Pequenos passos, grandes resultados."
]

QUOTE_FILE = "quote.txt"

def get_quote():
    try:
        res = requests.get("https://motivacional.top/api.php?acao=aleatoria", timeout=3)
        data = res.json()
        frase = data.get("dados", [{}])[0].get("frase", "")
        return frase if frase else random.choice(FRASES_FALLBACK)
    except:
        return random.choice(FRASES_FALLBACK)

def load_or_update_quote():
    hoje = date.today().isoformat()
    if os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            saved = f.readline().strip()
            frase = f.readline().strip()
        if saved == hoje:
            return frase
    frase = get_quote()
    with open(QUOTE_FILE, "w", encoding="utf-8") as f:
        f.write(f"{hoje}\n{frase}")
    return frase

st.title("🔑 Virada Financeira")
st.markdown(f'<div class="quote-card">{load_or_update_quote()}</div>', unsafe_allow_html=True)

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
    if pd.isna(v):
        return 0.0
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(v)
        except:
            return 0.0
    if isinstance(v, (int,float)):
        return float(v)
    return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_cores(n):
    cores = px.colors.qualitative.Vivid
    return [cores[i % len(cores)] for i in range(n)]

# =========================
# LEITURA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except:
    st.error("❌ Não foi possível carregar a planilha.")
    st.stop()

if df.shape[1] < 8:
    st.error("Estrutura da planilha insuficiente.")
    st.stop()

# =========================
# DETECÇÃO AUTOMÁTICA DOS BLOCOS
# =========================
def extrair_bloco(inicio):
    bloco = df.iloc[1:, inicio:inicio+4].copy()
    bloco = bloco.iloc[:, :4]
    bloco.columns = ["DATA","MES","DESCRICAO","VALOR"]
    return bloco

receitas = extrair_bloco(1)
despesas = extrair_bloco(5)

# =========================
# TRATAMENTO
# =========================
for base in [receitas, despesas]:
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()

# =========================
# MÉTRICAS
# =========================
st.subheader("📌 Visão Geral")
c1, c2, c3 = st.columns(3)

total_rec = receitas["VALOR"].sum()
total_des = despesas["VALOR"].sum()

c1.metric("💵 Receita Total", formato_real(total_rec))
c2.metric("💸 Despesa Total", formato_real(total_des))
c3.metric("⚖️ Saldo Geral", formato_real(total_rec - total_des))

st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["MES_ANO"] = (resumo["MES"] + "/" + resumo["ANO"].astype(str)).str.lower()
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")

# =========================
# BALANÇO FINANCEIRO
# =========================
expandir = st.toggle("🔎 Expandir gráfico completo", value=False)
hoje = datetime.now()

if expandir:
    resumo_plot = resumo[resumo["ANO"] == hoje.year].copy()
else:
    meses_a_mostrar = []
    for i in range(4):
        mes = hoje.month + i
        ano = hoje.year
        if mes > 12:
            mes -= 12
            ano += 1
        meses_a_mostrar.append((ano, mes))
    resumo_plot = resumo[resumo.apply(lambda x: (x["ANO"], x["MES_NUM"]) in meses_a_mostrar, axis=1)].copy()

if resumo_plot.empty:
    resumo_plot = resumo.copy()

st.subheader("📊 Balanço Financeiro")

fig = go.Figure()
cores_saldo = ["#3b82f6" if s>=0 else "#ef4444" for s in resumo_plot["SALDO"]]

fig.add_trace(go.Bar(
    x=resumo_plot["MES_ANO"].str.upper(),
    y=resumo_plot["RECEITA"],
    name="Receita",
    marker_color="#22c55e"
))

fig.add_trace(go.Bar(
    x=resumo_plot["MES_ANO"].str.upper(),
    y=resumo_plot["DESPESA"],
    name="Despesa",
    marker_color="#ef4444"
))

fig.add_trace(go.Bar(
    x=resumo_plot["MES_ANO"].str.upper(),
    y=resumo_plot["SALDO"],
    name="Saldo",
    marker_color=cores_saldo
))

fig.update_layout(height=450, barmode='group')
st.plotly_chart(fig, use_container_width=True)
