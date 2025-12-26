import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIG
# =========================
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

df = pd.read_excel(arquivo)

# =========================
# RECEITAS / DESPESAS
# =========================
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

despesas = df.iloc[1:, 6:10].copy()
despesas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

# =========================
# LIMPEZA
# =========================
for base in [receitas, despesas]:
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base["VALOR"] = limpar_valor(base["VALOR"])
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO_MES"] = base["DATA"].dt.to_period("M").dt.to_timestamp()
    base["MES_LABEL"] = base["DATA"].dt.strftime("%b/%Y").str.lower()

# =========================
# RESUMO GERAL
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

rec_m = receitas.groupby(["ANO_MES", "MES_LABEL"], as_index=False)["VALOR"].sum()
des_m = despesas.groupby(["ANO_MES", "MES_LABEL"], as_index=False)["VALOR"].sum()

resumo = pd.merge(
    rec_m, des_m,
    on=["ANO_MES", "MES_LABEL"],
    how="outer",
    suffixes=("_RECEITA", "_DESPESA")
).fillna(0)

resumo["SALDO"] = resumo["VALOR_RECEITA"] - resumo["VALOR_DESPESA"]
resumo = resumo.sort_values("ANO_MES")

# =========================
# CONTROLE EXPANDIR
# =========================
expandir = st.toggle("🔎 EXPANDIR TUDO", value=False)

hoje = datetime.now().replace(day=1)

if expandir:
    # Apenas meses do ANO CORRENTE
    resumo_plot = resumo[resumo["ANO_MES"].dt.year == hoje.year]
else:
    # Mês atual + 3 meses seguintes (com virada de ano)
    limite = hoje + pd.DateOffset(months=3)
    resumo_plot = resumo[
        (resumo["ANO_MES"] >= hoje) &
        (resumo["ANO_MES"] <= limite)
    ]

# =========================
# GRÁFICO ANUAL
# =========================
fig_anual = px.bar(
    resumo_plot,
    x="MES_LABEL",
    y=["VALOR_RECEITA", "VALOR_DESPESA", "SALDO"],
    barmode="group",
    labels={"value": "Valor (R$)", "MES_LABEL": "Mês"},
    text_auto=True
)

fig_anual.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")

fig_anual.update_traces(selector=dict(name="VALOR_RECEITA"), marker_color="#2ecc71")
fig_anual.update_traces(selector=dict(name="VALOR_DESPESA"), marker_color="#e74c3c")
fig_anual.update_traces(selector=dict(name="SALDO"), marker_color="#1abc9c")

st.plotly_chart(fig_anual, use_container_width=True)

# =========================
# SIDEBAR — MÊS
# =========================
st.sidebar.header("🔎 Análise Mensal Detalhada")

meses_disp = resumo["MES_LABEL"].tolist()
mes_atual_label = hoje.strftime("%b/%Y").lower()

mes_default = meses_disp.index(mes_atual_label) if mes_atual_label in meses_disp else 0

mes_sel = st.sidebar.selectbox("Selecione o mês", meses_disp, index=mes_default)

rec_mes = receitas[receitas["MES_LABEL"] == mes_sel]
des_mes = despesas[despesas["MES_LABEL"] == mes_sel]

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
    fig_r = px.bar(rec_mes, x="DESCRICAO", y="VALOR", text_auto=True)
    fig_r.update_traces(marker_color="#2ecc71", texttemplate="R$ %{y:,.2f}")
    st.plotly_chart(fig_r, use_container_width=True)

with g2:
    st.markdown("### 💸 Despesas do mês")
    fig_d = px.bar(des_mes, x="DESCRICAO", y="VALOR", text_auto=True)
    fig_d.update_traces(marker_color="#e74c3c", texttemplate="R$ %{y:,.2f}")
    st.plotly_chart(fig_d, use_container_width=True)
