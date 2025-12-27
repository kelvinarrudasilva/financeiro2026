import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import requests
import random
import os

# =========================
# CONFIGURAÇÃO GERAL
# =========================
st.set_page_config(
    page_title="🌑 Virada Financeira",
    page_icon="🌑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# ESTILO PREMIUM + FRASE
# =========================
st.markdown("""
<style>
:root {
    --bg: #0e0e11;
    --card: #16161d;
    --muted: #9ca3af;
    --accent: #22c55e;
}
html, body, [data-testid="stApp"] { background-color: var(--bg); }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1300px; }
h1 { font-weight: 700; letter-spacing: 0.5px; }
h2, h3 { font-weight: 600; }
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 18px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
[data-testid="metric-label"] { color: var(--muted); font-size: 0.85rem; }
[data-testid="metric-value"] { font-size: 1.6rem; font-weight: 700; }
section[data-testid="stSidebar"] { background-color: #0b0b10; border-right: 1px solid #1f1f2b; }
hr { border: none; height: 1px; background: #1f1f2b; margin: 2rem 0; }
.quote-card {
    background: linear-gradient(145deg, #1b1b24, #16161d);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #1f1f2b;
    margin-bottom: 1.5rem;
    font-size: 1.4rem;
    color: #9ca3af;
    font-style: italic;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FRASE MOTIVADORA DIÁRIA
# =========================
FRASES_FALLBACK = [
    "Grandes conquistas exigem dedicação.",
    "O sucesso vem para quem não desiste.",
    "A disciplina é o caminho para a liberdade financeira.",
    "Pequenos passos todos os dias levam a grandes resultados.",
    "Acredite no seu potencial e siga em frente.",
    "Cada desafio é uma oportunidade disfarçada.",
]

QUOTE_FILE = "quote.txt"

def get_portuguese_quote():
    try:
        res = requests.get("https://motivacional.top/api.php?acao=aleatoria", timeout=3)
        data = res.json()
        frase = data.get("dados", [{}])[0].get("frase", "")
        return frase if frase else random.choice(FRASES_FALLBACK)
    except:
        return random.choice(FRASES_FALLBACK)

def load_or_update_quote():
    hoje_str = date.today().isoformat()
    quote = ""
    if os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, "r", encoding="utf-8") as f:
            try:
                saved_date = f.readline().strip()
                quote = f.readline().strip()
            except:
                saved_date = ""
                quote = ""
        if saved_date != hoje_str:
            quote = get_portuguese_quote()
            with open(QUOTE_FILE, "w", encoding="utf-8") as f:
                f.write(f"{hoje_str}\n{quote}")
    else:
        quote = get_portuguese_quote()
        with open(QUOTE_FILE, "w", encoding="utf-8") as f:
            f.write(f"{hoje_str}\n{quote}")
    return quote

quote = load_or_update_quote()

# =========================
# CABEÇALHO
# =========================
st.title("🌑 Virada Financeira")
if quote:
    st.markdown(f'<div class="quote-card">{quote}</div>', unsafe_allow_html=True)

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
def limpar_valor(v):
    if pd.isna(v):
        return 0.0
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            return float(v)
        except:
            return 0.0
    if isinstance(v, (int,float)):
        return float(v)
    return 0.0

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_cores(n):
    cores = px.colors.qualitative.Vivid
    return [cores[i % len(cores)] for i in range(n)]

# =========================
# LEITURA PLANILHA
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
receitas.columns = ["DATA","MES","DESCRICAO","VALOR"]
despesas = df.iloc[1:, 6:10].copy()
despesas.columns = ["DATA","MES","DESCRICAO","VALOR"]

for base in [receitas, despesas]:
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
st.subheader("📌 Visão Geral")
c1, c2, c3 = st.columns(3)
c1.metric("💵 Receita Total", formato_real(receitas["VALOR"].sum()))
c2.metric("💸 Despesa Total", formato_real(despesas["VALOR"].sum()))
c3.metric("⚖️ Saldo Geral", formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum()))
st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})
resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["MES_ANO"] = (resumo["MES"] + "/" + resumo["ANO"].astype(str)).str.lower()
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")

# =========================
# BALANÇO FINANCEIRO
# =========================
expandir = st.toggle("🔎 Expandir gráfico completo", value=False)
hoje = datetime.now()

if expandir:
    resumo_plot = resumo[resumo["ANO"] == hoje.year].copy()
else:
    meses_a_mostrar = []
    for i in range(4):
        mes = hoje.month + i
        ano = hoje.year
        if mes > 12:
            mes -= 12
            ano += 1
        meses_a_mostrar.append((ano, mes))
    resumo_plot = resumo[resumo.apply(lambda x: (x["ANO"], x["MES_NUM"]) in meses_a_mostrar, axis=1)].copy()

if resumo_plot.empty:
    resumo_plot = resumo.copy()

st.subheader("📊 Balanço Financeiro")
fig = px.bar(
    resumo_plot,
    x="MES_ANO",
    y=["RECEITA","DESPESA","SALDO"],
    barmode="group",
    text_auto=True
)
fig.update_layout(height=420, margin=dict(l=20,r=20,t=40,b=20), legend_title=None)
fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")
fig.update_traces(selector=dict(name="RECEITA"), marker_color="#22c55e")
fig.update_traces(selector=dict(name="DESPESA"), marker_color="#ef4444")
fig.update_traces(selector=dict(name="SALDO"), marker_color="#3b82f6")
st.plotly_chart(fig, use_container_width=True)

# =========================
# SESSION_STATE PARA MÊS SELECIONADO
# =========================
if "mes_sel" not in st.session_state:
    st.session_state["mes_sel"] = hoje.strftime("%b").lower() + f"/{hoje.year}"

# =========================
# SIDEBAR
# =========================
st.sidebar.header("📆 Análise Mensal")
meses_unicos = resumo["MES_ANO"].unique()
try:
    idx = list(meses_unicos).index(st.session_state["mes_sel"])
except ValueError:
    idx = 0

mes_sel = st.sidebar.selectbox("Mês", meses_unicos, index=idx, key="mes_sel_select")
st.session_state["mes_sel"] = mes_sel
mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

# =========================
# BOTÃO PRÓXIMO MÊS ESTÁVEL
# =========================
def avancar_mes(mes, ano):
    datas = sorted(resumo["DATA_CHAVE"].unique())
    for i, d in enumerate(datas):
        if d.year == ano and d.month == datetime.strptime(mes, "%b").month:
            indice = (i + 1) % len(datas)
            nova_data = datas[indice]
            return nova_data.strftime("%b").lower(), nova_data.year
    return mes, ano

col_titulo, col_botao = st.columns([8,1])
with col_titulo:
    st.subheader(f"📆 Detalhamento — {st.session_state['mes_sel']}")
with col_botao:
    if st.button("➡ Próximo mês"):
        mes_txt, ano_sel = avancar_mes(mes_txt, ano_sel)
        st.session_state["mes_sel"] = f"{mes_txt}/{ano_sel}"

# =========================
# DADOS DO MÊS
# =========================
rec_mes = receitas[(receitas["ANO"]==ano_sel)&(receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel)&(despesas["MES"]==mes_txt)]

# =========================
# MÉTRICAS DETALHADAS
# =========================
d1, d2, d3 = st.columns(3)
d1.metric("💰 Receitas", formato_real(rec_mes["VALOR"].sum()))
d2.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
d3.metric("⚖️ Saldo", formato_real(rec_mes["VALOR"].sum()-des_mes["VALOR"].sum()))

# =========================
# COMPOSIÇÃO DO MÊS
# =========================
st.subheader("📌 Composição do mês")
col_r, col_d = st.columns(2)

with col_r:
    if not rec_mes.empty:
        fig_r = px.pie(
            rec_mes,
            values="VALOR",
            names="DESCRICAO",
            hole=0.55,
            title="💰 Receitas",
            color_discrete_sequence=gerar_cores(len(rec_mes))
        )
        fig_r.update_traces(texttemplate="%{label}<br>R$ %{value:,.2f}", textposition="inside")
        fig_r.update_layout(showlegend=True, margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Nenhuma receita no mês.")

with col_d:
    if not des_mes.empty:
        fig_d = px.pie(
            des_mes,
            values="VALOR",
            names="DESCRICAO",
            hole=0.55,
            title="💸 Despesas",
            color_discrete_sequence=gerar_cores(len(des_mes))
        )
        fig_d.update_traces(texttemplate="%{label}<br>R$ %{value:,.2f}", textposition="inside")
        fig_d.update_layout(showlegend=True, margin=dict(t=50, b=20, l=20, r=20))
        st.plotly_chart(fig_d, use_container_width=True)
    else:
        st.info("Nenhuma despesa no mês.")
