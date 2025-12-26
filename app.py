import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(
    page_title="Virada Financeira",
    page_icon="🌑",
    layout="wide"
)

st.title("🌑 Virada Financeira")
st.caption("Visão anual para decisões grandes. Zoom mensal para decisões certas.")

# ================= FUNÇÕES =================
def limpar_valor(col):
    col = col.astype(str)
    col = col.str.replace(r"[^\d,.-]", "", regex=True)
    col = col.str.replace(".", "", regex=False)
    col = col.str.replace(",", ".", regex=False)
    return pd.to_numeric(col, errors="coerce").fillna(0)

def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ================= UPLOAD =================
arquivo = st.file_uploader(
    "📂 Envie sua planilha financeira",
    type=["xlsx"]
)

if arquivo:
    df = pd.read_excel(arquivo, sheet_name=0)

    # ---------- RECEITAS ----------
    receitas = df.iloc[:, 1:5].copy()
    receitas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

    # ---------- DESPESAS ----------
    despesas = df.iloc[:, 6:10].copy()
    despesas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

    for t in [receitas, despesas]:
        t.dropna(how="all", inplace=True)
        t["MES"] = t["MES"].astype(str).str.strip()
        t = t[t["MES"].str.upper() != "MÊS"]
        t["VALOR"] = limpar_valor(t["VALOR"])

    # ================= RESUMO ANUAL =================
    rec_anual = receitas.groupby("MES", as_index=False)["VALOR"].sum()
    rec_anual.rename(columns={"VALOR": "RECEITA"}, inplace=True)

    des_anual = despesas.groupby("MES", as_index=False)["VALOR"].sum()
    des_anual.rename(columns={"VALOR": "DESPESA"}, inplace=True)

    resumo = pd.merge(rec_anual, des_anual, on="MES", how="outer").fillna(0)
    resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]

    ordem = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    resumo["ordem"] = resumo["MES"].str.lower().map({m:i for i,m in enumerate(ordem)})
    resumo = resumo.sort_values("ordem").drop(columns="ordem")

    # ================= KPIs =================
    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Receita Anual", brl(resumo["RECEITA"].sum()))
    c2.metric("💸 Despesa Anual", brl(resumo["DESPESA"].sum()))
    c3.metric("⚖️ Saldo Geral", brl(resumo["SALDO"].sum()))

    st.divider()

    # ================= GRÁFICO ANUAL =================
    st.subheader("📊 Balanço Anual — Receita x Despesa")

    fig_bar = px.bar(
        resumo,
        x="MES",
        y=["RECEITA", "DESPESA"],
        barmode="group",
        template="plotly_dark",
        text_auto=".2f"
    )

    fig_bar.update_traces(
        textposition="inside",
        insidetextanchor="middle"
    )

    fig_bar.update_yaxes(
        tickprefix="R$ ",
        tickformat=",.2f"
    )

    fig_bar.update_layout(
        uniformtext_minsize=10,
        uniformtext_mode="hide"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ================= FILTRO MENSAL =================
    st.subheader("🔎 Análise Mensal Detalhada")

    meses_disponiveis = sorted(
        set(receitas["MES"].unique()).union(despesas["MES"].unique())
    )

    mes_sel = st.selectbox(
        "Selecione o mês",
        meses_disponiveis
    )

    rec_mes = receitas[receitas["MES"] == mes_sel]
    des_mes = despesas[despesas["MES"] == mes_sel]

    # ================= GRÁFICOS DETALHADOS =================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 💰 Receitas — {mes_sel}")
        if rec_mes.empty:
            st.info("Nenhuma receita neste mês.")
        else:
            fig_rec = px.bar(
                rec_mes,
                x="DESCRICAO",
                y="VALOR",
                template="plotly_dark",
                text_auto=".2f"
            )
            fig_rec.update_traces(textposition="inside")
            fig_rec.update_yaxes(tickprefix="R$ ")
            st.plotly_chart(fig_rec, use_container_width=True)

    with col2:
        st.markdown(f"### 💸 Despesas — {mes_sel}")
        if des_mes.empty:
            st.info("Nenhuma despesa neste mês.")
        else:
            fig_des = px.bar(
                des_mes,
                x="DESCRICAO",
                y="VALOR",
                template="plotly_dark",
                text_auto=".2f"
            )
            fig_des.update_traces(textposition="inside")
            fig_des.update_yaxes(tickprefix="R$ ")
            st.plotly_chart(fig_des, use_container_width=True)

    st.divider()

    # ================= TABELA MENSAL =================
    st.subheader("📋 Resumo Financeiro do Mês")

    resumo_mes = pd.DataFrame({
        "Tipo": ["Receitas", "Despesas", "Saldo"],
        "Valor": [
            rec_mes["VALOR"].sum(),
            des_mes["VALOR"].sum(),
            rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()
        ]
    })

    resumo_mes["Valor"] = resumo_mes["Valor"].apply(brl)
    st.table(resumo_mes)

else:
    st.info("Envie o arquivo **VIRADA FINANCEIRA - Copia.xlsx** para iniciar.")
