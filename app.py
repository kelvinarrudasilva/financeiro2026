import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(
    page_title="Virada Financeira",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Virada Financeira")
st.caption("Onde o caos vira clareza — e o saldo respira.")

# ================= UPLOAD =================
arquivo = st.file_uploader(
    "📂 Envie sua planilha financeira",
    type=["xlsx"]
)

# ================= FUNÇÕES =================
def limpar_valor(coluna):
    coluna = coluna.astype(str)
    coluna = coluna.str.replace(r"[^\d,.-]", "", regex=True)
    coluna = coluna.str.replace(".", "", regex=False)
    coluna = coluna.str.replace(",", ".", regex=False)
    return pd.to_numeric(coluna, errors="coerce").fillna(0)

def formatar_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ================= APP =================
if arquivo:
    df = pd.read_excel(arquivo, sheet_name=0)

    # -------- RECEITAS --------
    receitas = df.iloc[:, 1:5].copy()
    receitas.columns = ["DATA", "MES", "NOME", "VALOR"]

    # -------- DESPESAS --------
    despesas = df.iloc[:, 6:10].copy()
    despesas.columns = ["DATA", "MES", "NOME", "VALOR"]

    # -------- LIMPEZA PESADA --------
    for t in [receitas, despesas]:
        t.dropna(how="all", inplace=True)
        t["MES"] = t["MES"].astype(str).str.strip()
        t = t[t["MES"].str.upper() != "MÊS"]
        t["VALOR"] = limpar_valor(t["VALOR"])

    # ================= RESUMO MENSAL =================
    rec = receitas.groupby("MES", as_index=False)["VALOR"].sum()
    rec.rename(columns={"VALOR": "RECEITA"}, inplace=True)

    des = despesas.groupby("MES", as_index=False)["VALOR"].sum()
    des.rename(columns={"VALOR": "DESPESA"}, inplace=True)

    resumo = pd.merge(rec, des, on="MES", how="outer")

    # 🔥 BLINDAGEM FINAL
    resumo["RECEITA"] = pd.to_numeric(resumo["RECEITA"], errors="coerce").fillna(0)
    resumo["DESPESA"] = pd.to_numeric(resumo["DESPESA"], errors="coerce").fillna(0)
    resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]

    # -------- ORDENA MESES --------
    ordem = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    resumo["ordem"] = resumo["MES"].str.lower().map({m:i for i,m in enumerate(ordem)})
    resumo = resumo.sort_values("ordem").drop(columns="ordem")

    # ================= KPIs =================
    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Receita Total", formatar_real(resumo["RECEITA"].sum()))
    c2.metric("💸 Despesa Total", formatar_real(resumo["DESPESA"].sum()))
    c3.metric("⚖️ Saldo Geral", formatar_real(resumo["SALDO"].sum()))

    st.divider()

    # ================= TABELA =================
    st.subheader("📊 Resumo Mensal")

    vis = resumo.copy()
    for c in ["RECEITA", "DESPESA", "SALDO"]:
        vis[c] = vis[c].apply(formatar_real)

    st.dataframe(vis, use_container_width=True)

    # ================= GRÁFICOS =================
    st.plotly_chart(
        px.bar(
            resumo,
            x="MES",
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
            x="MES",
            y="SALDO",
            markers=True,
            template="plotly_dark",
            title="Evolução do Saldo"
        ),
        use_container_width=True
    )

    # ================= ALERTAS =================
    st.subheader("🚨 Meses no Vermelho")

    neg = resumo[resumo["SALDO"] < 0]

    if neg.empty:
        st.success("Nenhum mês no vermelho. Gestão afiada.")
    else:
        for _, r in neg.iterrows():
            st.error(f"{r['MES']}: déficit de {formatar_real(abs(r['SALDO']))}")

else:
    st.info("Envie o arquivo **VIRADA FINANCEIRA - Copia.xlsx** para iniciar.")
