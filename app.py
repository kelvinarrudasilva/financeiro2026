import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="Painel Financeiro Pessoal",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Painel Financeiro Pessoal")
st.caption("Dinheiro sob controle. Mente em paz.")

# ---------------- UPLOAD ----------------
arquivo = st.file_uploader(
    "📂 Envie seu arquivo Excel financeiro",
    type=["xlsx"]
)

if arquivo:
    xls = pd.ExcelFile(arquivo)
    abas = {aba.lower(): aba for aba in xls.sheet_names}

    # ---------------- IDENTIFICAÇÃO AUTOMÁTICA ----------------
    aba_receitas = next((abas[a] for a in abas if "receita" in a), None)
    aba_despesas = next((abas[a] for a in abas if "despesa" in a), None)

    if not aba_receitas or not aba_despesas:
        st.error("❌ Não foi possível identificar as abas de Receitas e Despesas.")
        st.stop()

    receitas = pd.read_excel(xls, sheet_name=aba_receitas)
    despesas = pd.read_excel(xls, sheet_name=aba_despesas)

    # ---------------- PADRONIZAÇÃO ----------------
    for df in [receitas, despesas]:
        df.columns = df.columns.str.upper().str.strip()
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

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

    col1.metric("💵 Receita Total", f"R$ {resumo['RECEITA'].sum():,.2f}")
    col2.metric("💸 Despesa Total", f"R$ {resumo['DESPESA'].sum():,.2f}")
    col3.metric("⚖️ Saldo Geral", f"R$ {resumo['SALDO'].sum():,.2f}")

    st.divider()

    # ---------------- TABELA ----------------
    st.subheader("📊 Resumo Mensal")
    st.dataframe(resumo, use_container_width=True)

    # ---------------- GRÁFICO RECEITA x DESPESA ----------------
    fig_bar = px.bar(
        resumo,
        x="MÊS",
        y=["RECEITA", "DESPESA"],
        barmode="group",
        template="plotly_dark",
        title="Receita x Despesa por Mês"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- GRÁFICO SALDO ----------------
    fig_line = px.line(
        resumo,
        x="MÊS",
        y="SALDO",
        markers=True,
        template="plotly_dark",
        title="Evolução do Saldo"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ---------------- DESPESAS POR CATEGORIA ----------------
    st.subheader("🧾 Onde seu dinheiro está indo")

    despesas_cat = despesas.groupby("NOME")["VALOR"].sum().reset_index()

    fig_pie = px.pie(
        despesas_cat,
        names="NOME",
        values="VALOR",
        hole=0.45,
        template="plotly_dark"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # ---------------- ALERTAS ----------------
    st.subheader("🚨 Alertas")

    negativos = resumo[resumo["SALDO"] < 0]

    if not negativos.empty:
        for _, row in negativos.iterrows():
            st.error(f"No mês **{row['MÊS']}** você gastou mais do que ganhou.")
    else:
        st.success("Todos os meses fecharam no positivo. Controle absoluto.")

else:
    st.info("Envie o arquivo Excel para iniciar o painel.")
