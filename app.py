import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIG GERAL
# =========================
st.set_page_config(
    page_title="🌑 Virada Financeira",
    page_icon="🌑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# ESTILO PREMIUM
# =========================
st.markdown("""
<style>
:root {
    --bg: #0e0e11;
    --card: #16161d;
    --muted: #9ca3af;
    --accent: #22c55e;
}

html, body, [data-testid="stApp"] {
    background-color: var(--bg);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1300px;
}

/* TITULOS */
h1 {
    font-weight: 700;
    letter-spacing: 0.5px;
}
h2, h3 {
    font-weight: 600;
}

/* MÉTRICAS */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
[data-testid="metric-label"] {
    color: var(--muted);
    font-size: 0.85rem;
}
[data-testid="metric-value"] {
    font-size: 1.6rem;
    font-weight: 700;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #0b0b10;
    border-right: 1px solid #1f1f2b;
}

/* DIVISOR */
hr {
    border: none;
    height: 1px;
    background: #1f1f2b;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# CABEÇALHO
# =========================
st.title("🌑 Virada Financeira")
st.caption("O dinheiro sob a luz da consciência.")

# =========================
# PLANILHA GOOGLE DRIVE
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

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
# LEITURA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except:
    st.error("❌ Não foi possível carregar a planilha.")
    st.stop()

# =========================
# BASES
# =========================
receitas = df.iloc[1:, 1:5].copy()
receitas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

despesas = df.iloc[1:, 6:10].copy()
despesas.columns = ["DATA", "MES", "DESCRICAO", "VALOR"]

for base in [receitas, despesas]:
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base["VALOR"] = limpar_valor(base["VALOR"])
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()

# =========================
# MÉTRICAS (DESKTOP 3 / MOBILE STACK)
# =========================
st.subheader("📌 Visão Geral")

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
c2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
c3.metric(
    "⚖️ Saldo Geral",
    formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum())
)

st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum()
rec_m.rename(columns={"VALOR":"RECEITA"}, inplace=True)

des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum()
des_m.rename(columns={"VALOR":"DESPESA"}, inplace=True)

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["MES_ANO"] = resumo["MES"] + "/" + resumo["ANO"].astype(str)

# =========================
# CONTROLE DE VISÃO
# =========================
expandir = st.toggle("🔎 Mostrar histórico completo", value=False)

hoje = datetime.now()

if expandir:
    resumo_plot = resumo.copy()
else:
    resumo_plot = resumo[
        (resumo["ANO"] > hoje.year) |
        ((resumo["ANO"] == hoje.year) & (resumo["MES_NUM"] >= hoje.month))
    ]

if resumo_plot.empty:
    resumo_plot = resumo.copy()

# =========================
# GRÁFICO PRINCIPAL
# =========================
st.subheader("📊 Balanço Financeiro")

fig = px.bar(
    resumo_plot,
    x="MES_ANO",
    y=["RECEITA","DESPESA","SALDO"],
    barmode="group",
    text_auto=True
)

fig.update_layout(
    height=420,
    margin=dict(l=20,r=20,t=40,b=20),
    legend_title=None
)

fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")
fig.update_traces(selector=dict(name="RECEITA"), marker_color="#22c55e")
fig.update_traces(selector=dict(name="DESPESA"), marker_color="#ef4444")
fig.update_traces(selector=dict(name="SALDO"), marker_color="#3b82f6")

st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# SIDEBAR — MOBILE OK
# =========================
st.sidebar.header("📆 Análise Mensal")

resumo["CHAVE"] = resumo["MES"] + "/" + resumo["ANO"].astype(str)
chave_atual = hoje.strftime("%b").lower() + f"/{hoje.year}"

idx = resumo["CHAVE"].tolist().index(chave_atual) if chave_atual in resumo["CHAVE"].tolist() else 0

mes_sel = st.sidebar.selectbox("Mês", resumo["CHAVE"].unique(), index=idx)
mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

rec_mes = receitas[(receitas["ANO"]==ano_sel)&(receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel)&(despesas["MES"]==mes_txt)]

# =========================
# DETALHAMENTO
# =========================
st.subheader(f"📆 Detalhamento — {mes_sel}")

d1, d2, d3 = st.columns(3)
d1.metric("💰 Receitas", formato_real(rec_mes["VALOR"].sum()))
d2.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
d3.metric("⚖️ Saldo", formato_real(rec_mes["VALOR"].sum()-des_mes["VALOR"].sum()))

# =========================
# GRÁFICOS MENSAIS (MOBILE FIRST)
# =========================
st.subheader("📌 Composição do mês")

if not rec_mes.empty:
    st.plotly_chart(
        px.pie(rec_mes, values="VALOR", names="DESCRICAO", hole=0.45),
        use_container_width=True
    )

if not des_mes.empty:
    st.plotly_chart(
        px.pie(des_mes, values="VALOR", names="DESCRICAO", hole=0.45),
        use_container_width=True
    )
