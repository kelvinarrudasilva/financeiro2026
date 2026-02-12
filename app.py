import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import random

st.set_page_config(page_title="🚀 Virada Financeira ELITE", page_icon="💎", layout="wide")

# =========================
# FRASES
# =========================
FRASES = [
    "Riqueza é consistência invisível.",
    "Disciplina financeira é liberdade futura.",
    "Você não está organizando dinheiro. Está construindo patrimônio.",
    "Controle hoje. Poder amanhã."
]

st.title("💎 Virada Financeira ELITE 2026")
st.caption(random.choice(FRASES))

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
    try:
        if isinstance(v, str):
            v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(v)
    except:
        return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def preparar(df):
    df = df.copy().dropna(axis=1, how="all")

    col_data = None
    col_valor = None
    col_desc = None

    for col in df.columns:
        tentativa = pd.to_datetime(df[col], errors="coerce")
        if tentativa.notna().sum() > 3:
            df[col] = tentativa
            col_data = col
            break

    for col in df.columns:
        tentativa = df[col].apply(limpar_valor)
        if tentativa.sum() != 0:
            df[col] = tentativa
            col_valor = col
            break

    outras = [c for c in df.columns if c not in [col_data, col_valor]]
    if outras:
        col_desc = outras[0]

    if not col_data or not col_valor:
        return pd.DataFrame()

    base = pd.DataFrame()
    base["DATA"] = df[col_data]
    base["VALOR"] = df[col_valor]
    base["DESC"] = df[col_desc] if col_desc else "Sem descrição"

    base["ANO"] = base["DATA"].dt.year
    base["MES"] = base["DATA"].dt.month

    return base.dropna(subset=["DATA"])

# =========================
# LEITURA
# =========================
df = pd.read_excel(PLANILHA_URL)
meio = len(df.columns)//2

receitas = preparar(df.iloc[:, :meio])
despesas = preparar(df.iloc[:, meio:])

rec = receitas.groupby(["ANO","MES"], as_index=False)["VALOR"].sum()
des = despesas.groupby(["ANO","MES"], as_index=False)["VALOR"].sum()

resumo = pd.merge(rec, des, on=["ANO","MES"], how="outer", suffixes=("_REC","_DES")).fillna(0)
resumo["SALDO"] = resumo["VALOR_REC"] - resumo["VALOR_DES"]

ano_atual = datetime.now().year
mes_atual = datetime.now().month
proximo_mes = mes_atual + 1 if mes_atual < 12 else 1

res_ano = resumo[resumo["ANO"]==ano_atual]

receita_ano = res_ano["VALOR_REC"].sum()
despesa_ano = res_ano["VALOR_DES"].sum()
saldo_ano = res_ano["SALDO"].sum()
saldo_restante = res_ano[res_ano["MES"] >= proximo_mes]["SALDO"].sum()

# INVESTIMENTO
try:
    inv_df = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO", header=None)
    investido = limpar_valor(inv_df.iloc[13,1])
except:
    investido = 0

patrimonio_atual = investido + saldo_ano

# =========================
# SCORE FINANCEIRO
# =========================
taxa = (saldo_ano/receita_ano*100) if receita_ano>0 else 0
consumo = (despesa_ano/receita_ano*100) if receita_ano>0 else 100

score = 0
score += min(taxa,40)
score += max(0,40-consumo/2)
score += 20 if saldo_ano>0 else 0
score = round(min(score,100))

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("💰 Receita Ano", formato_real(receita_ano))
c2.metric("💸 Despesa Ano", formato_real(despesa_ano))
c3.metric("🏦 Saldo Ano", formato_real(saldo_ano))
c4.metric("📈 Investido", formato_real(investido))
c5.metric("💎 Patrimônio Atual", formato_real(patrimonio_atual))

st.divider()

# =========================
# SCORE VISUAL
# =========================
st.subheader("🏆 Score Financeiro")

fig_score = go.Figure(go.Indicator(
    mode="gauge+number",
    value=score,
    gauge={'axis': {'range': [0, 100]}},
))
fig_score.update_layout(height=300, template="plotly")
st.plotly_chart(fig_score, use_container_width=True)

# =========================
# PROJEÇÃO ATÉ DEZEMBRO
# =========================
st.subheader("🔮 Projeção até Dezembro")

media_mensal = res_ano["SALDO"].mean()
meses_restantes = 12 - mes_atual

conservador = patrimonio_atual + (media_mensal * meses_restantes)
otimista = patrimonio_atual + (media_mensal * 1.1 * meses_restantes)
agressivo = patrimonio_atual + (media_mensal * 1.2 * meses_restantes)

colA,colB,colC = st.columns(3)
colA.metric("Conservador", formato_real(conservador))
colB.metric("Otimista", formato_real(otimista))
colC.metric("Agressivo", formato_real(agressivo))

# =========================
# EVOLUÇÃO PATRIMÔNIO
# =========================
st.subheader("📊 Evolução do Patrimônio")

res_ano = res_ano.sort_values("MES")
res_ano["ACUMULADO"] = res_ano["SALDO"].cumsum() + investido

fig_line = px.line(res_ano, x="MES", y="ACUMULADO")
fig_line.update_layout(template="plotly",
                       plot_bgcolor="rgba(0,0,0,0)",
                       paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_line, use_container_width=True)

# =========================
# MAPA DE CONSUMO
# =========================
st.subheader("🧠 Mapa de Consumo")

fig_donut = go.Figure(data=[go.Pie(
    labels=["Despesa","Saldo"],
    values=[despesa_ano, saldo_ano],
    hole=.6
)])
fig_donut.update_layout(template="plotly",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig_donut, use_container_width=True)
