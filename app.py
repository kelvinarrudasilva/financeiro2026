import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🌑 Virada Financeira", layout="wide")

st.title("🌑 Virada Financeira")
st.caption("O dinheiro sob a luz da consciência.")

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
# UPLOAD
# =========================
arquivo = st.file_uploader("📂 Envie sua planilha financeira", type=["xlsx"])
if not arquivo:
    st.stop()

# =========================
# LEITURA BRUTA
# =========================
df = pd.read_excel(arquivo)

# =========================
# RECEITAS (COLUNAS ESQUERDA)
# =========================
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

# =========================
# DESPESAS (COLUNAS DIREITA)
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
    base["MES"] = base["MES"].astype(str).str.lower().str.strip()

# =========================
# RESUMO ANUAL
# =========================
total_receita = receitas["VALOR"].sum()
total_despesa = despesas["VALOR"].sum()
saldo_geral = total_receita - total_despesa

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Anual", formato_real(total_receita))
c2.metric("💸 Despesa Anual", formato_real(total_despesa))
c3.metric("⚖️ Saldo Geral", formato_real(saldo_geral))

# =========================
# BALANÇO ANUAL
# =========================
st.subheader("📊 Balanço Anual — Receita x Despesa")

rec_m = receitas.groupby("MES", as_index=False)["VALOR"].sum()
des_m = despesas.groupby("MES", as_index=False)["VALOR"].sum()

resumo = pd.merge(
    rec_m, des_m,
    on="MES",
    how="outer",
    suffixes=("_RECEITA", "_DESPESA")
).fillna(0)

resumo["SALDO"] = resumo["VALOR_RECEITA"] - resumo["VALOR_DESPESA"]

fig_anual = px.bar(
    resumo,
    x="MES",
    y=["VALOR_RECEITA", "VALOR_DESPESA", "SALDO"],
    barmode="group",
    color_discrete_sequence=["#2ecc71", "#e74c3c", "#27ae60"],
    labels={"value": "Valor (R$)", "MES": "Mês"},
    text_auto=True
)

fig_anual.update_traces(
    texttemplate="R$ %{y:,.2f}",
    textposition="inside"
)

st.plotly_chart(fig_anual, use_container_width=True)

# =========================
# SIDEBAR — MÊS
# =========================
st.sidebar.header("🔎 Análise Mensal Detalhada")

meses = sorted(resumo["MES"].unique().tolist())
mes_atual = datetime.now().strftime("%b").lower()
mes_default = meses.index(mes_atual) if mes_atual in meses else 0

mes_sel = st.sidebar.selectbox(
    "Selecione o mês",
    meses,
    index=mes_default
)

rec_mes = receitas[receitas["MES"] == mes_sel]
des_mes = despesas[despesas["MES"] == mes_sel]

# =========================
# DETALHAMENTO
# =========================
st.subheader(f"📆 Detalhamento — {mes_sel}")

c4, c5, c6 = st.columns(3)
c4.metric("Receitas", formato_real(rec_mes["VALOR"].sum()))
c5.metric("Despesas", formato_real(des_mes["VALOR"].sum()))
c6.metric("Saldo do Mês", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

# =========================
# GRÁFICOS MENSAIS
# =========================
g1, g2 = st.columns(2)

with g1:
    st.markdown("### 💰 Receitas do mês")
    fig_r = px.pie(
        rec_mes,
        values="VALOR",
        names="DESCRICAO",
        hole=0.45
    )
    fig_r.update_traces(
        texttemplate="R$ %{value:,.2f}",
        textposition="inside"
    )
    st.plotly_chart(fig_r, use_container_width=True, key="rec_mes")

with g2:
    st.markdown("### 💸 Despesas do mês")
    fig_d = px.pie(
        des_mes,
        values="VALOR",
        names="DESCRICAO",
        hole=0.45
    )
    fig_d.update_traces(
        texttemplate="R$ %{value:,.2f}",
        textposition="inside"
    )
    st.plotly_chart(fig_d, use_container_width=True, key="des_mes")
