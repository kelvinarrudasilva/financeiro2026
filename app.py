import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Painel Financeiro Pessoal",
    page_icon="💰",
    layout="wide"
)

# ---------------- TEMA DARK ----------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
</style>
""", unsafe_allow_html=True)

st.title("💰 Painel Financeiro Pessoal")
st.caption("Controle total. Visão clara. Decisão consciente.")

# ---------------- UPLOAD DO ARQUIVO ----------------
arquivo = st.file_uploader(
    "📂 Envie seu arquivo financeiro (Excel)",
    type=["xlsx"]
)

if arquivo:
    receitas = pd.read_excel(arquivo, sheet_name="Receitas")
    despesas = pd.read_excel(arquivo, sheet_name="Despesas")

    # Padronização
    receitas["VALOR"] = pd.to_numeric(receitas["VALOR"])
    despesas["VALOR"] = pd.to_numeric(despesas["VALOR"])

    # ---------------- RESUMO MENSAL ----------------
    resumo_receitas = receitas.groupby("MÊS")["VALOR"].sum().reset_index(name="RECEITA")
    resumo_despesas = despesas.groupby("MÊS")["VALOR"].sum().reset_index(name="DESPESA")

    resumo = pd.merge(
        resumo_receitas,
        resumo_despesas,
        on="MÊS",
        how="outer"
    ).fillna(0)

    resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]

    # ---------------- KPIs ----------------
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💵 Receita Total",
        f"R$ {resumo['RECEITA'].sum():,.2f}"
    )

    col2.metric(
        "💸 Despesa Total",
        f"R$ {resumo['DESPESA'].sum():,.2f}"
    )

    col3.metric(
        "⚖️ Saldo Geral",
        f"R$ {resumo['SALDO'].sum():,.2f}"
    )

    st.divider()

    # ---------------- TABELA RESUMO ----------------
    st.subheader("📊 Resumo Mensal")
    st.dataframe(
        resumo,
        use_container_width=True
    )

    # ---------------- GRÁFICO RECEITA x DESPESA ----------------
    fig_bar = px.bar(
        resumo,
        x="MÊS",
        y=["RECEITA", "DESPESA"],
        barmode="group",
        title="Receita x Despesa por Mês",
        template="plotly_dark"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- GRÁFICO SALDO ----------------
    fig_saldo = px.line(
        resumo,
        x="MÊS",
        y="SALDO",
        markers=True,
        title="Evolução do Saldo Mensal",
        template="plotly_dark"
    )
    st.plotly_chart(fig_saldo, use_container_width=True)

    # ---------------- DESPESAS POR CATEGORIA ----------------
    st.subheader("🧾 Distribuição de Despesas")

    despesas_categoria = despesas.groupby("NOME")["VALOR"].sum().reset_index()

    fig_pizza = px.pie(
        despesas_categoria,
        names="NOME",
        values="VALOR",
        hole=0.5,
        template="plotly_dark"
    )
    st.plotly_chart(fig_pizza, use_container_width=True)

    # ---------------- ALERTAS INTELIGENTES ----------------
    st.subheader("🚨 Alertas Financeiros")

    meses_negativos = resumo[resumo["SALDO"] < 0]

    if not meses_negativos.empty:
        for _, row in meses_negativos.iterrows():
            st.error(f"No mês **{row['MÊS']}** você gastou mais do que ganhou.")
    else:
        st.success("Todos os meses estão com saldo positivo. Excelente controle.")

else:
    st.info("Envie o arquivo Excel para iniciar o painel.")
