import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =========================
# CONFIG PREMIUM
# =========================
st.set_page_config(
    page_title="🌑 Virada Financeira",
    page_icon="🌑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* ===== PREMIUM STYLE ===== */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
h1, h2, h3 { letter-spacing: 0.5px; }
[data-testid="metric-container"] {
    background: #111;
    border-radius: 14px;
    padding: 16px;
}
[data-testid="metric-label"] { font-size: 0.85rem; }
[data-testid="metric-value"] { font-size: 1.4rem; }
</style>
""", unsafe_allow_html=True)

st.title("🌑 Virada Financeira")
st.caption("O dinheiro sob a luz da consciência.")

# =========================
# GOOGLE DRIVE
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
# MÉTRICAS (RESPONSIVAS)
# =========================
with st.container():
    c1, c2, c3 = st.columns([1,1,1], gap="large")
    c1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
    c2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
    c3.metric("⚖️ Saldo Geral", formato_real(
        receitas["VALOR"].sum() - despesas["VALOR"].sum()
    ))

st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"].sum()
rec_m.rename(columns={"VALOR": "RECEITA"}, inplace=True)

des_m = despesas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"].sum()
des_m.rename(columns={"VALOR": "DESPESA"}, inplace=True)

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["MES_ANO"] = resumo["MES"] + "/" + resumo["ANO"].astype(str)

# =========================
# CONTROLE
# =========================
expandir = st.toggle("🔎 Mostrar histórico completo", value=False)

hoje = datetime.now()
if not expandir:
    resumo_plot = resumo[
        (resumo["ANO"] > hoje.year) |
        ((resumo["ANO"] == hoje.year) & (resumo["MES_NUM"] >= hoje.month))
    ]
else:
    resumo_plot = resumo.copy()

if resumo_plot.empty:
    resumo_plot = resumo.copy()

# =========================
# GRÁFICO PRINCIPAL (MOBILE OK)
# =========================
fig = px.bar(
    resumo_plot,
    x="MES_ANO",
    y=["RECEITA","DESPESA","SALDO"],
    barmode="group",
    text_auto=True
)

fig.update_layout(
    height=420,
    legend_title=None,
    margin=dict(l=20,r=20,t=40,b=20)
)

fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")
fig.update_traces(selector=dict(name="RECEITA"), marker_color="#2ecc71")
fig.update_traces(selector=dict(name="DESPESA"), marker_color="#e74c3c")
fig.update_traces(selector=dict(name="SALDO"), marker_color="#3498db")

st.subheader("📊 Balanço Financeiro")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# SIDEBAR (CELULAR FRIENDLY)
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

c4, c5, c6 = st.columns(3)
c4.metric("💰 Receitas", formato_real(rec_mes["VALOR"].sum()))
c5.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
c6.metric("⚖️ Saldo", formato_real(rec_mes["VALOR"].sum()-des_mes["VALOR"].sum()))

# =========================
# GRÁFICOS MENSAIS (MOBILE FIRST)
# =========================
st.markdown("### 📌 Composição do mês")

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
