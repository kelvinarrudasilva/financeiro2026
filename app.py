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
# FRASE MOTIVADORA DIÁRIA
# =========================
FRASES_FALLBACK = [
    "Grandes conquistas exigem dedicação.",
    "O sucesso vem para quem não desiste.",
    "A disciplina é o caminho para a liberdade financeira.",
    "Pequenos passos todos os dias levam a grandes resultados.",
    "Acredite no seu potencial e siga em frente.",
    "Cada desafio é uma oportunidade disfarçada.",
]

QUOTE_FILE = "quote.txt"

def get_portuguese_quote():
    try:
        res = requests.get("https://motivacional.top/api.php?acao=aleatoria", timeout=3)
        data = res.json()
        frase = data.get("dados", [{}])[0].get("frase", "")
        return frase if frase else random.choice(FRASES_FALLBACK)
    except:
        return random.choice(FRASES_FALLBACK)

def load_or_update_quote():
    hoje_str = date.today().isoformat()
    quote = ""
    if os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            try:
                saved_date = f.readline().strip()
                quote = f.readline().strip()
            except:
                saved_date = ""
                quote = ""
        if saved_date != hoje_str:
            quote = get_portuguese_quote()
            with open(QUOTE_FILE, "w", encoding="utf-8") as f:
                f.write(f"{hoje_str}\n{quote}")
    else:
        quote = get_portuguese_quote()
        with open(QUOTE_FILE, "w", encoding="utf-8") as f:
            f.write(f"{hoje_str}\n{quote}")
    return quote

quote = load_or_update_quote()

st.title("🔑 Virada Financeira")
if quote:
    st.markdown(f'<div class="quote-card">{quote}</div>', unsafe_allow_html=True)

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
    if isinstance(v, (int,float)):
        return float(v)
    return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_cores(n):
    cores = px.colors.qualitative.Vivid
    return [cores[i % len(cores)] for i in range(n)]

# =========================
# LEITURA PLANILHA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except:
    st.error("❌ Não foi possível carregar a planilha.")
    st.stop()

# =========================
# BASES (CORRIGIDO PARA 9 COLUNAS)
# =========================
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA","MES","DESCRICAO","VALOR"]

despesas = df.iloc[1:, 5:9].copy()  # <<< CORREÇÃO AQUI
despesas.columns = ["DATA","MES","DESCRICAO","VALOR"]

for base in [receitas, despesas]:
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()

# =========================
# (RESTO DO APP PERMANECE 100% IGUAL)
# =========================
