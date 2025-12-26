import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="🌑 Virada Financeira",
    layout="wide"
)

st.title("🌑 Virada Financeira")
st.caption("O dinheiro sob a luz da consciência.")

# =========================
# UPLOAD
# =========================
arquivo = st.file_uploader(
    "📂 Envie sua planilha financeira",
    type=["xlsx"]
)

if not arquivo:
    st.stop()

# =========================
# LEITURA FLEXÍVEL
# =========================
xls = pd.ExcelFile(arquivo)
df = pd.concat(
    [pd.read_excel(xls, sheet_name=aba) for aba in xls.sheet_names],
    ignore_index=True
)

df.columns = df.columns.str.upper().str.strip()

colunas_necessarias = {"DATA", "DESCRICAO", "VALOR", "TIPO"}
if not colunas_necessarias.issubset(df.columns):
    st.error("❌ A planilha precisa ter as colunas: DATA, DESCRICAO, VALOR, TIPO")
    st.stop()

df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")
df["TIPO"] = df["TIPO"].str.upper().str.strip()

df = df.dropna(subset=["DATA", "VALOR"])

df["MES"] = df["DATA"].dt.month
df["ANO"] = df["DATA"].dt.year

# =========================
# SIDEBAR — FILTRO MENSAL
# =========================
st.sidebar.header("🔎 Análise Mensal Detalhada")

mes_atual = datetime.now().month
mapa_meses = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
}

mes_selecionado = st.sidebar.selectbox(
    "Selecione o mês",
    options=list(mapa_meses.keys()),
    format_func=lambda x: mapa_meses[x],
    index=mes_atual - 1
)

df_mes = df[df["MES"] == mes_selecionado]
rec_mes = df_mes[df_mes["TIPO"] == "RECEITA"]
des_mes = df_mes[df_mes["TIPO"] == "DESPESA"]

# =========================
# INDICADORES ANUAIS
# =========================
receita_anual = df[df["TIPO"] == "RECEITA"]["VALOR"].sum()
despesa_anual = df[df["TIPO"] == "DESPESA"]["VALOR"].sum()
saldo_geral = receita_anual - despesa_anual

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Anual", f"R$ {receita_anual:,.2f}")
c2.metric("💸 Despesa Anual", f"R$ {despesa_anual:,.2f}")
c3.metric("⚖️ Saldo Geral", f"R$ {saldo_geral:,.2f}")

# =========================
# 📆 DETALHAMENTO MENSAL (PRIMEIRO)
# =========================
st.subheader(f"📆 Detalhamento — {mapa_meses[mes_selecionado]}")

g1, g2 = st.columns(2)

with g1:
    st.markdown("### 💰 Receitas do mês — ranking")
    if rec_mes.empty:
        st.info("Nenhuma receita registrada.")
    else:
        fig_r = px.bar(
            rec_mes.sort_values("VALOR"),
            x="VALOR",
            y="DESCRICAO",
            orientation="h",
            text="VALOR"
        )
        fig_r.update_traces(
            marker_color="#2ecc71",
            texttemplate="R$ %{text:,.2f}",
            textposition="outside"
        )
        fig_r.update_layout(xaxis_tickprefix="R$ ", xaxis_tickformat=",.2f")
        st.plotly_chart(fig_r, use_container_width=True)

with g2:
    st.markdown("### 💸 Despesas do mês — ranking")
    if des_mes.empty:
        st.info("Nenhuma despesa registrada.")
    else:
        fig_d = px.bar(
            des_mes.sort_values("VALOR"),
            x="VALOR",
            y="DESCRICAO",
            orientation="h",
            text="VALOR"
        )
        fig_d.update_traces(
            marker_color="#e74c3c",
            texttemplate="R$ %{text:,.2f}",
            textposition="outside"
        )
        fig_d.update_layout(xaxis_tickprefix="R$ ", xaxis_tickformat=",.2f")
        st.plotly_chart(fig_d, use_container_width=True)

# =========================
# 📊 BALANÇO ANUAL
# =========================
st.subheader("📊 Balanço Anual — Receita x Despesa")

resumo = (
    df.groupby(["ANO", "TIPO"])["VALOR"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

resumo["SALDO"] = resumo.get("RECEITA", 0) - resumo.get("DESPESA", 0)

fig_b = px.bar(
    resumo,
    x="ANO",
    y=["RECEITA", "DESPESA", "SALDO"],
    barmode="group",
    text_auto=".2s",
    color_discrete_map={
        "RECEITA": "#2ecc71",
        "DESPESA": "#e74c3c",
        "SALDO": "#27ae60"
    }
)

fig_b.update_layout(yaxis_tickprefix="R$ ", yaxis_tickformat=",.2f")
st.plotly_chart(fig_b, use_container_width=True)
