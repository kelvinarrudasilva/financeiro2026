import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="🚀 Virada Financeira PRO", page_icon="💰", layout="wide")

# =========================
# FRASE
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Consistência cria patrimônio invisível.",
    "Quem controla o dinheiro controla o futuro.",
    "Riqueza é organização repetida."
]

st.title("🚀 Virada Financeira PRO 2026")
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

if receitas.empty or despesas.empty:
    st.error("Erro na leitura da planilha.")
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

saldo_restante = res_ano[res_ano["MES"] >= proximo_mes]["SALDO"].sum()

# =========================
# INVESTIMENTO
# =========================
try:
    inv_df = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO", header=None)
    investido = limpar_valor(inv_df.iloc[13,1])
except:
    investido = 0

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("💵 Receita no Ano", formato_real(receita_ano))
col2.metric("💸 Despesa no Ano", formato_real(despesa_ano))
col3.metric("🏦 Saldo no Ano", formato_real(saldo_ano))
col4.metric("🧭 Saldo Restante", formato_real(saldo_restante))
col5.metric("📈 Investido", formato_real(investido))

# =========================
# MÉTRICAS AVANÇADAS
# =========================
st.divider()
st.subheader("📊 Inteligência Financeira")

taxa = (saldo_ano/receita_ano*100) if receita_ano>0 else 0
patrimonio_projetado = investido + saldo_restante

colA,colB,colC = st.columns(3)
colA.metric("📌 Taxa de Economia", f"{taxa:.1f}%")
colB.metric("💎 Patrimônio Projetado", formato_real(patrimonio_projetado))

if receita_ano > 0:
    consumo = despesa_ano/receita_ano*100
else:
    consumo = 0

if consumo > 85:
    colC.metric("⚠️ Risco", "Alto 🔴")
elif consumo > 70:
    colC.metric("⚠️ Risco", "Moderado 🟡")
else:
    colC.metric("⚠️ Risco", "Controlado 🟢")

# =========================
# VISÃO ANUAL
# =========================
st.divider()
st.subheader("📈 Evolução Mensal do Ano")

resumo_anual = res_ano.copy()
resumo_anual = resumo_anual[resumo_anual["MES"].between(1,12)]
resumo_anual["MES"] = resumo_anual["MES"].astype(int)

meses = {
    1:"Jan",2:"Fev",3:"Mar",4:"Abr",
    5:"Mai",6:"Jun",7:"Jul",8:"Ago",
    9:"Set",10:"Out",11:"Nov",12:"Dez"
}

resumo_anual["MES_NOME"] = resumo_anual["MES"].map(meses)

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
# DESPESAS DO PRÓXIMO MÊS
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
