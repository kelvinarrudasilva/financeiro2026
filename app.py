import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="Painel Financeiro Pessoal",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Painel Financeiro Pessoal")
st.caption("Quando os números ficam claros, as decisões ficam leves.")

# ================= UPLOAD =================
arquivo = st.file_uploader(
    "📂 Envie seu arquivo Excel financeiro",
    type=["xlsx"]
)

# ================= FUNÇÕES =================
def limpar_valor(coluna):
    coluna = coluna.astype(str)
    coluna = coluna.str.replace(r"[^\d,.-]", "", regex=True)
    coluna = coluna.str.replace(".", "", regex=False)
    coluna = coluna.str.replace(",", ".", regex=False)
    return pd.to_numeric(coluna, errors="coerce").fillna(0)

def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ================= APP =================
if arquivo:
    # Lê a primeira aba
    df = pd.read_excel(arquivo, sheet_name=0)

    # -------- RECEITAS (B:E) --------
    receitas = df.iloc[:, 1:5].copy()
    receitas.columns = ["DATA", "MÊS", "NOME", "VALOR"]

    # -------- DESPESAS (G:J) --------
    despesas = df.iloc[:, 6:10].copy()
    despesas.columns = ["DATA", "MÊS", "NOME", "VALOR"]

    # -------- LIMPEZA --------
    for tabela in [receitas, despesas]:
        tabela.dropna(how="all", inplace=True)
        tabela = tabela[tabela["MÊS"].astype(str).str.lower() != "mês"]
        tabela["VALOR"] = limpar_valor(tabela["VALOR"])

    # -------- RESUMO MENSAL (BLINDADO) --------
    resumo_receitas = (
        receitas.groupby("MÊS", as_index=False)["VALOR"]
        .sum()
        .rename(columns={"VALOR": "RECEITA"})
    )

    resumo_despesas = (
        despesas.groupby("MÊS", as_index=False)["VALOR"]
        .sum()
        .rename(columns={"VALOR": "DESPESA"})
    )

    resumo = resumo_receitas.merge(
        resumo_despesas,
        on="MÊS",
        how="outer"
    ).fillna(0)

    resumo["RECEITA"] = resumo["RECEITA"].astype(float)
    resumo["DESPESA"] = resumo["DESPESA"].astype(float)
    resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]

    # -------- ORDENA MESES --------
    ordem = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    resumo["ordem"] = resumo["MÊS"].str.lower().map({m:i for i,m in enumerate(ordem)})
    resumo = resumo.sort_values("ordem").drop(columns="ordem")

    # ================= KPIs =================
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Receita Total", formatar_real(resumo["RECEITA"].sum()))
    col2.metric("💸 Despesa Total", formatar_real(resumo["DESPESA"].sum()))
    col3.metric("⚖️ Saldo Geral", formatar_real(resumo["SALDO"].sum()))

    st.divider()

    # ================= TABELA =================
    st.subheader("📊 Resumo Mensal")

    resumo_vis = resumo.copy()
    for c in ["RECEITA","DESPESA","SALDO"]:
        resumo_vis[c] = resumo_vis[c].apply(formatar_real)

    st.dataframe(resumo_vis, use_container_width=True)

    # ================= GRÁFICOS =================
    st.plotly_chart(
        px.bar(
            resumo,
            x="MÊS",
            y=["RECEITA","DESPESA"],
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
        use_container_width=True
    )

    # ================= DESPESAS POR CATEGORIA =================
    st.subheader("🧾 Para onde vai seu dinheiro")

    despesas_cat = despesas.groupby("NOME", as_index=False)["VALOR"].sum()

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

    # ================= ALERTAS =================
    st.subheader("🚨 Alertas Financeiros")

    negativos = resumo[resumo["SALDO"] < 0]

    if negativos.empty:
        st.success("Nenhum mês no vermelho. Controle absoluto.")
    else:
        for _, r in negativos.iterrows():
            st.error(
                f"No mês **{r['MÊS']}**, saldo negativo de {formatar_real(abs(r['SALDO']))}"
            )

else:
    st.info("Envie o arquivo Excel para iniciar o painel.")
