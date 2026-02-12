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
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1300px; }
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
    "Grandes conquistas exigem dedicação.",
    "Disciplina constrói liberdade.",
    "Pequenos passos geram grandes resultados.",
    "Você não está atrasado. Está construindo.",
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
    if isinstance(v, (int, float)):
        return float(v)
    return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def normalizar_colunas(df):
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df

def preparar_base(base):
    base = normalizar_colunas(base)

    col_data = [c for c in base.columns if "DATA" in c][0]
    col_valor = [c for c in base.columns if "VALOR" in c][0]
    col_desc = [c for c in base.columns if "NOME" in c or "DESCR" in c][0]

    base = base[[col_data, col_desc, col_valor]].copy()
    base.columns = ["DATA", "DESCRICAO", "VALOR"]

    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base = base.dropna(subset=["DATA"])

    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.upper()

    return base

# =========================
# LEITURA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except:
    st.error("Erro ao carregar planilha.")
    st.stop()

df = normalizar_colunas(df)

# Divide automaticamente em duas metades
meio = len(df.columns) // 2
df_rec = df.iloc[:, :meio].copy()
df_des = df.iloc[:, meio:].copy()

receitas = preparar_base(df_rec)
despesas = preparar_base(df_des)

# =========================
# MÉTRICAS
# =========================
st.subheader("📌 Visão Geral")
c1, c2, c3 = st.columns(3)
c1.metric("Receita Total", formato_real(receitas["VALOR"].sum()))
c2.metric("Despesa Total", formato_real(despesas["VALOR"].sum()))
c3.metric("Saldo Geral", formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum()))

st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")
resumo["MES_ANO"] = resumo["DATA_CHAVE"].dt.strftime("%b/%Y").str.upper()

# =========================
# GRÁFICO PRINCIPAL
# =========================
st.subheader("📊 Balanço Financeiro")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["RECEITA"],
    name="Receita",
    marker_color="#22c55e"
))

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["DESPESA"],
    name="Despesa",
    marker_color="#ef4444"
))

fig.add_trace(go.Scatter(
    x=resumo["MES_ANO"],
    y=resumo["SALDO"],
    mode="lines+markers",
    name="Saldo",
    line=dict(color="#facc15", width=3)
))

fig.update_layout(barmode="group", height=450)
st.plotly_chart(fig, use_container_width=True)

# =========================
# SELETOR DE MÊS
# =========================
mes_sel = st.selectbox("Escolha o mês", resumo["MES_ANO"].tolist())

mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

rec_mes = receitas[(receitas["ANO"]==ano_sel) & (receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel) & (despesas["MES"]==mes_txt)]

st.subheader(f"📆 Detalhamento — {mes_sel}")

d1, d2, d3 = st.columns(3)
d1.metric("Receitas", formato_real(rec_mes["VALOR"].sum()))
d2.metric("Despesas", formato_real(des_mes["VALOR"].sum()))
d3.metric("Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))
