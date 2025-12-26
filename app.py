import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="🌑 Virada Financeira",
    layout="wide"
)

st.title("🌑 Virada Financeira")
st.caption("O dinheiro sob a luz da consciência.")

# =========================
# LINK DA PLANILHA (GOOGLE DRIVE)
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

# =========================
# FUNÇÕES
# =========================
def limpar_valor(col):
    return (
        col.astype(str)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# LEITURA DA PLANILHA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except Exception as e:
    st.error("❌ Não foi possível carregar a planilha do Google Drive.")
    st.stop()

# =========================
# RECEITAS
# =========================
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

# =========================
# DESPESAS
# =========================
despesas = df.iloc[1:, 6:10].copy()
despesas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

# =========================
# LIMPEZA
# =========================
for base in [receitas, despesas]:
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base["VALOR"] = limpar_valor(base["VALOR"])
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()

# =========================
# RESUMO GERAL
# =========================
total_receita = receitas["VALOR"].sum()
total_despesa = despesas["VALOR"].sum()
saldo_geral = total_receita - total_despesa

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Total", formato_real(total_receita))
c2.metric("💸 Despesa Total", formato_real(total_despesa))
c3.metric("⚖️ Saldo Geral", formato_real(saldo_geral))

# =========================
# BALANÇO TEMPORAL
# =========================
st.subheader("📊 Balanço — Receita x Despesa")

rec_m = receitas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"].sum()
rec_m.rename(columns={"VALOR": "RECEITA"}, inplace=True)

des_m = despesas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"].sum()
des_m.rename(columns={"VALOR": "DESPESA"}, inplace=True)

resumo = pd.merge(
    rec_m, des_m,
    on=["ANO", "MES_NUM", "MES"],
    how="outer"
).fillna(0)

resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO", "MES_NUM"])

# =========================
# CONTROLE DE EXIBIÇÃO
# =========================
expandir = st.toggle("🔎 EXPANDIR TUDO", value=False)

hoje = datetime.now()
ano_atual = hoje.year
mes_atual = hoje.month

if expandir:
    resumo_plot = resumo[resumo["ANO"] == ano_atual]
else:
    resumo_plot = resumo[
        (resumo["ANO"] > ano_atual) |
        ((resumo["ANO"] == ano_atual) & (resumo["MES_NUM"] >= mes_atual))
    ].head(4)

if resumo_plot.empty:
    resumo_plot = resumo.copy()

resumo_plot["MES_ANO"] = resumo_plot["MES"] + "/" + resumo_plot["ANO"].astype(str)

# =========================
# GRÁFICO
# =========================
fig = px.bar(
    resumo_plot,
    x="MES_ANO",
    y=["RECEITA", "DESPESA", "SALDO"],
    barmode="group",
    text_auto=True,
    labels={"value": "Valor (R$)", "MES_ANO": "Mês/Ano"}
)

fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")
fig.update_traces(selector=dict(name="RECEITA"), marker_color="#2ecc71")
fig.update_traces(selector=dict(name="DESPESA"), marker_color="#e74c3c")
fig.update_traces(selector=dict(name="SALDO"), marker_color="#3498db")

st.plotly_chart(fig, use_container_width=True)

# =========================
# SIDEBAR — MÊS ATUAL CORRETO
# =========================
st.sidebar.header("🔎 Análise Mensal")

resumo["CHAVE"] = resumo["MES"] + "/" + resumo["ANO"].astype(str)

chave_atual = hoje.strftime("%b").lower() + f"/{ano_atual}"

idx = (
    resumo["CHAVE"].tolist().index(chave_atual)
    if chave_atual in resumo["CHAVE"].tolist()
    else 0
)

mes_sel = st.sidebar.selectbox(
    "Selecione o mês",
    resumo["CHAVE"].unique(),
    index=idx
)

ano_sel = int(mes_sel.split("/")[1])
mes_txt = mes_sel.split("/")[0]

rec_mes = receitas[(receitas["ANO"] == ano_sel) & (receitas["MES"] == mes_txt)]
des_mes = despesas[(despesas["ANO"] == ano_sel) & (despesas["MES"] == mes_txt)]

# =========================
# DETALHAMENTO
# =========================
st.subheader(f"📆 Detalhamento — {mes_sel}")

c4, c5, c6 = st.columns(3)
c4.metric("💰 Receitas", formato_real(rec_mes["VALOR"].sum()))
c5.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
c6.metric("⚖️ Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))
