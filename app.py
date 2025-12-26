import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="Painel Financeiro Pessoal",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Painel Financeiro Pessoal")
st.caption("Ver o dinheiro com clareza muda decisões.")

# ================= UPLOAD =================
arquivo = st.file_uploader(
    "📂 Envie seu arquivo Excel financeiro",
    type=["xlsx"]
)

# ================= FUNÇÃO ROBUSTA DE LIMPEZA =================
def limpar_valor(coluna):
    coluna = coluna.astype(str)
    coluna = coluna.str.replace(r"[^\d,.-]", "", regex=True)
    coluna = coluna.str.replace(".", "", regex=False)
    coluna = coluna.str.replace(",", ".", regex=False)
    return pd.to_numeric(coluna, errors="coerce").fillna(0)

# ================= APP =================
if arquivo:
    # Lê a PRIMEIRA aba (qualquer nome)
    df = pd.read_excel(arquivo, sheet_name=0)

    # ---------- RECEITAS (B:E) ----------
    receitas = df.iloc[:, 1:5].copy()
    receitas.columns = ["DATA", "MÊS", "NOME", "VALOR"]

    # ---------- DESPESAS (G:J) ----------
    despesas = df.iloc[:, 6:10].copy()
    despesas.columns = ["DATA", "MÊS", "NOME", "VALOR"]

    # ---------- LIMPEZA ----------
    for tabela in [receitas, despesas]:
        tabela.dropna(how="all", inplace=True)
        tabela["VALOR"] = limpar_valor(tabela["VALOR"])

    # ---------- RESUMO MENSAL ----------
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

    # ================= KPIs =================
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Receita Total", f"R$ {resumo['RECEITA'].sum():,.2f}")
    col2.metric("💸 Despesa Total", f"R$ {resumo['DESPESA'].sum():,.2f}")
    col3.metric("⚖️ Saldo Geral", f"R$ {resumo['SALDO'].sum():,.2f}")

    st.divider()

    # ================= TABELA =================
    st.subheader("📊 Resumo Mensal")
    st.dataframe(resumo, use_container_width=True)

    # ================= GRÁFICOS =================
    st.plotly_chart(
        px.bar(
            resumo,
            x="MÊS",
            y=["RECEITA", "DESPESA"],
            barmode="group",
            template="plotly_dark",
            title="Receita x Despesa por Mês"
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
        use
