import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="💰 Virada Financeira", page_icon="💰", layout="wide")

# =========================
# FRASES
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Consistência cria patrimônio invisível.",
    "Quem controla o dinheiro controla o futuro."
]

st.title("💰 Virada Financeira 2026")
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
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(v)
        except:
            return 0.0
    return float(v)

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def detectar_colunas(df):
    df.columns = df.columns.str.upper().str.strip()
    data_col = [c for c in df.columns if "DATA" in c]
    desc_col = [c for c in df.columns if "DESC" in c]
    valor_col = [c for c in df.columns if "VALOR" in c]

    if data_col and desc_col and valor_col:
        return data_col[0], desc_col[0], valor_col[0]
    else:
        return None, None, None

def preparar(df):
    data_col, desc_col, valor_col = detectar_colunas(df)
    if not data_col:
        return pd.DataFrame()

    base = df[[data_col, desc_col, valor_col]].copy()
    base.columns = ["DATA", "DESC", "VALOR"]

    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")

    base["ANO"] = base["DATA"].dt.year
    base["MES"] = base["DATA"].dt.month

    return base.dropna(subset=["DATA"])

# =========================
# LEITURA
# =========================
df = pd.read_excel(PLANILHA_URL)

meio = len(df.columns) // 2
receitas = preparar(df.iloc[:, :meio])
despesas = preparar(df.iloc[:, meio:])

# Segurança extra
if receitas.empty or despesas.empty:
    st.error("Erro ao identificar colunas DATA / DESC / VALOR na planilha.")
    st.stop()

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

# 🔥 SALDO RESTANTE baseado no PRÓXIMO MÊS
saldo_restante = res_ano[res_ano["MES"] >= proximo_mes]["SALDO"].sum()

# INVESTIMENTO
try:
    inv_df = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO", header=None)
    investido = limpar_valor(inv_df.iloc[13,1])
except:
    investido = 0

# =========================
# MÉTRICAS
# =========================
col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("💵 Receita no Ano", formato_real(receita_ano))
col2.metric("💸 Despesa no Ano", formato_real(despesa_ano))
col3.metric("🏦 Saldo no Ano", formato_real(saldo_ano))
col4.metric("🧭 Saldo Restante", formato_real(saldo_restante))
col5.metric("📈 Investido", formato_real(investido))

# =========================
# VISÃO GERAL ANUAL
# =========================
st.divider()
st.subheader("📊 Visão Geral do Ano")

resumo_anual = resumo[resumo["ANO"]==ano_atual].copy()
resumo_anual["MES_NOME"] = resumo_anual["MES"].apply(
    lambda x: datetime(1900,x,1).strftime("%b")
)

fig = go.Figure()

fig.add_bar(
    x=resumo_anual["MES_NOME"],
    y=resumo_anual["SALDO"],
    text=resumo_anual["SALDO"].apply(formato_real),
    textposition="inside"
)

fig.update_layout(
    template="plotly",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# DESPESAS DO MÊS PRE-SELECIONADO
# =========================
st.divider()
st.subheader("💸 Despesas do Próximo Mês")

despesas_mes = despesas[
    (despesas["ANO"]==ano_atual) &
    (despesas["MES"]==proximo_mes)
]

if not despesas_mes.empty:
    agrup = despesas_mes.groupby("DESC", as_index=False)["VALOR"].sum()

    fig2 = px.bar(
        agrup,
        x="VALOR",
        y="DESC",
        orientation="h",
        text=agrup["VALOR"].apply(formato_real)
    )

    fig2.update_traces(textposition="inside")

    fig2.update_layout(
        template="plotly",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(autorange="reversed")
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Sem despesas registradas para o próximo mês.")
