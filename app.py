import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Financeiro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================
# LEITURA DA PLANILHA
# =====================
arquivo = "VIRADA FINANCEIRA.xlsx"
df_raw = pd.read_excel(arquivo, header=None)

# RECEITAS
receitas = df_raw.iloc[1:4, 1:5]
receitas.columns = ["Data", "Mes", "Descricao", "Valor"]
receitas["Tipo"] = "Receita"

# DESPESAS
despesas = df_raw.iloc[1:6, 6:10]
despesas.columns = ["Data", "Mes", "Descricao", "Valor"]
despesas["Tipo"] = "Despesa"

# BASE FINAL
df = pd.concat([receitas, despesas])
df.dropna(inplace=True)

df["Data"] = pd.to_datetime(df["Data"])
df["Valor"] = df["Valor"].astype(float)

# =====================
# SIDEBAR - FILTROS
# =====================
st.sidebar.title("📅 Filtros")

meses = sorted(df["Mes"].unique())
mes_selecionado = st.sidebar.selectbox("Selecione o mês", meses)

df_mes = df[df["Mes"] == mes_selecionado]

# =====================
# KPIs PRINCIPAIS
# =====================
receita_total = df_mes[df_mes["Tipo"] == "Receita"]["Valor"].sum()
despesa_total = df_mes[df_mes["Tipo"] == "Despesa"]["Valor"].sum()
saldo = receita_total - despesa_total

c1, c2, c3 = st.columns(3)
c1.metric("💰 Receitas", f"R$ {receita_total:,.2f}")
c2.metric("💸 Despesas", f"R$ {despesa_total:,.2f}")
c3.metric("📊 Saldo", f"R$ {saldo:,.2f}")

st.divider()

# =====================
# GRÁFICOS
# =====================
col1, col2 = st.columns(2)

with col1:
    fig_pizza = px.pie(
        df_mes,
        names="Tipo",
        values="Valor",
        title="Receitas x Despesas"
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

with col2:
    fig_barras = px.bar(
        df_mes,
        x="Descricao",
        y="Valor",
        color="Tipo",
        title="Detalhamento do Mês"
    )
    st.plotly_chart(fig_barras, use_container_width=True)

# =====================
# VISÃO ANUAL
# =====================
st.divider()
st.subheader("📆 Panorama Geral do Ano")

df_ano = df.groupby(["Mes", "Tipo"])["Valor"].sum().reset_index()

fig_ano = px.bar(
    df_ano,
    x="Mes",
    y="Valor",
    color="Tipo",
    barmode="group",
    title="Receitas e Despesas por Mês"
)

st.plotly_chart(fig_ano, use_container_width=True)

# =====================
# TABELA DETALHADA
# =====================
st.subheader("📋 Lançamentos do Mês")
st.dataframe(
    df_mes.sort_values("Data"),
    use_container_width=True
)
