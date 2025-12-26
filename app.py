import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="🌑 Virada Financeira",
    layout="wide"
)

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
arquivo = st.file_uploader(
    "📂 Envie sua planilha financeira",
    type=["xlsx"]
)

if not arquivo:
    st.stop()

# =========================
# LEITURA
# =========================
df = pd.read_excel(arquivo)

# =========================
# RECEITAS / DESPESAS
# =========================
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA", "MES_TXT", "DESCRICAO", "VALOR"]

despesas = df.iloc[1:, 6:10].copy()
despesas.columns = ["DATA", "MES_TXT", "DESCRICAO", "VALOR"]

# =========================
# LIMPEZA
# =========================
for base in [receitas, despesas]:
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base["VALOR"] = limpar_valor(base["VALOR"])
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()
    base["MES_ANO"] = base["MES"] + "/" + base["ANO"].astype(str)

# =========================
# RESUMO GERAL
# =========================
total_receita = receitas["VALOR"].sum()
total_despesa = despesas["VALOR"].sum()
saldo_geral = total_receita - total_despesa

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Total", formato_real(total_receita))
c2.metric("💸 Despesa Total", formato_real(total_despesa))
c3.metric("⚖️ Saldo Geral", formato_real(saldo_geral))

# =========================
# BALANÇO CONSOLIDADO
# =========================
st.subheader("📊 Balanço — Receita x Despesa")

rec_m = receitas.groupby(
    ["ANO", "MES_NUM", "MES", "MES_ANO"], as_index=False
)["VALOR"].sum().rename(columns={"VALOR": "RECEITA"})

des_m = despesas.groupby(
    ["ANO", "MES_NUM", "MES", "MES_ANO"], as_index=False
)["VALOR"].sum().rename(columns={"VALOR": "DESPESA"})

resumo = pd.merge(
    rec_m, des_m,
    on=["ANO", "MES_NUM", "MES", "MES_ANO"],
    how="outer"
).fillna(0)

resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO", "MES_NUM"])

# =========================
# CONTROLE DE VISUALIZAÇÃO
# =========================
expandir = st.toggle("🔎 EXPANDIR TUDO", value=False)

hoje = datetime.now()
ano_atual = hoje.year
mes_atual = hoje.month

if expandir:
    # todos os meses do ANO ATUAL que existirem na planilha
    resumo_plot = resumo[resumo["ANO"] == ano_atual]
else:
    # mês atual + próximos 3 (mesmo atravessando ano)
    resumo_plot = resumo[
        (resumo["ANO"] > ano_atual) |
        ((resumo["ANO"] == ano_atual) & (resumo["MES_NUM"] >= mes_atual))
    ].head(4)

# fallback de segurança
if resumo_plot.empty:
    resumo_plot = resumo.copy()

# =========================
# GRÁFICO PRINCIPAL
# =========================
fig_anual = px.bar(
    resumo_plot,
    x="MES_ANO",
    y=["RECEITA", "DESPESA", "SALDO"],
    barmode="group",
    labels={"value": "Valor (R$)", "MES_ANO": "Mês/Ano"},
    text_auto=True
)

fig_anual.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")
fig_anual.update_traces(selector=dict(name="RECEITA"), marker_color="#2ecc71")
fig_anual.update_traces(selector=dict(name="DESPESA"), marker_color="#e74c3c")
fig_anual.update_traces(selector=dict(name="SALDO"), marker_color="#3498db")

st.plotly_chart(fig_anual, use_container_width=True)

# =========================
# SIDEBAR — MÊS ATUAL
# =========================
st.sidebar.header("🔎 Análise Mensal")

lista_meses = resumo["MES_ANO"].unique().tolist()
mes_atual_chave = hoje.strftime("%b").lower() + "/" + str(ano_atual)

if mes_atual_chave in lista_meses:
    idx_padrao = lista_meses.index(mes_atual_chave)
else:
    idx_padrao = 0

mes_sel = st.sidebar.selectbox(
    "Selecione o mês",
    lista_meses,
    index=idx_padrao
)

mes_txt, ano_txt = mes_sel.split("/")
ano_sel = int(ano_txt)

rec_mes = receitas[(receitas["MES"] == mes_txt) & (receitas["ANO"] == ano_sel)]
des_mes = despesas[(despesas["MES"] == mes_txt) & (despesas["ANO"] == ano_sel)]

# =========================
# DETALHAMENTO
# =========================
st.subheader(f"📆 Detalhamento — {mes_sel}")

c4, c5, c6 = st.columns(3)
c4.metric("💰 Receitas", formato_real(rec_mes["VALOR"].sum()))
c5.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
c6.metric("⚖️ Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

# =========================
# GRÁFICOS MENSAIS
# =========================
g1, g2 = st.columns(2)

with g1:
    fig_r = px.pie(
        rec_mes,
        names="DESCRICAO",
        values="VALOR",
        title="💰 Receitas do mês",
        hole=0.4
    )
    fig_r.update_traces(texttemplate="R$ %{value:,.2f}")
    st.plotly_chart(fig_r, use_container_width=True)

with g2:
    fig_d = px.pie(
        des_mes,
        names="DESCRICAO",
        values="VALOR",
        title="💸 Despesas do mês",
        hole=0.4
    )
    fig_d.update_traces(texttemplate="R$ %{value:,.2f}")
    st.plotly_chart(fig_d, use_container_width=True)
