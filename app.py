import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Painel Financeiro Pessoal",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Painel Financeiro Pessoal")
st.caption("Ver o dinheiro com clareza muda decisões.")

arquivo = st.file_uploader(
    "📂 Envie seu arquivo Excel financeiro",
    type=["xlsx"]
)

if arquivo:
    xls = pd.ExcelFile(arquivo)

    abas = {aba.lower(): aba for aba in xls.sheet_names}

    aba_receitas = None
    aba_despesas = None

    for a in abas:
        if "receita" in a:
            aba_receitas = abas[a]
        if "despesa" in a:
            aba_despesas = abas[a]

    if not aba_receitas or not aba_despesas:
        st.error("❌ O arquivo precisa ter uma aba de Receitas e outra de Despesas.")
        st.stop()

    receitas = pd.read_excel(xls, sheet_name=aba_receitas)
    despesas = pd.read_excel(xls, sheet_name=aba_despesas)

    for df in [receitas, despesas]:
        df.columns = df.columns.str.upper().str.strip()
        df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0)

    resumo = (
        receitas.groupby("MÊS")["VALOR"].sum()
        .rename("RECEITA")
        .to_frame()
        .join(
            despesas.groupby("MÊS")["VALOR"].sum().rename("DESPESA"),
            how="outer"
        )
        .fillna(0)
        .reset_index()
    )

    resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Receita Total", f"R$ {resumo['RECEITA'].sum():,.2f}")
    col2.metric("💸 Despesa Total", f"R$ {resumo['DESPESA'].sum():,.2f}")
    col3.metric("⚖️ Saldo Geral", f"R$ {resumo['SALDO'].sum():,.2f}")

    st.divider()
    st.subheader("📊 Resumo Mensal")
    st.dataframe(resumo, use_container_width=True)

    st.plotly_chart(
        px.bar(
            resumo,
            x="MÊS",
            y=["RECEITA", "DESPESA"],
            barmode="group",
            template="plotly_dark",
            title="Receita x Despesa"
        ),
        use_container_width=True
    )

    st.plotly_chart(
        px.line(
            resumo,
            x="MÊS",
            y="SALDO",
            markers=True,
            template="plotly_dark",
            title="Evolução do Saldo"
        ),
        use_container_width=True
    )

    st.subheader("🧾 Para onde vai seu dinheiro")

    despesas_cat = despesas.groupby("NOME")["VALOR"].sum().reset_index()

    st.plotly_chart(
        px.pie(
            despesas_cat,
            names="NOME",
            values="VALOR",
            hole=0.45,
            template="plotly_dark"
        ),
        use_container_width=True
    )

    negativos = resumo[resumo["SALDO"] < 0]
    st.subheader("🚨 Alertas")

    if negativos.empty:
        st.success("Nenhum mês no vermelho. Disciplina em dia.")
    else:
        for _, row in negativos.iterrows():
            st.error(f"No mês **{row['MÊS']}**, você gastou mais do que ganhou.")

else:
    st.info("Envie o arquivo Excel para iniciar.")
