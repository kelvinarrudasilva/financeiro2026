import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO MODERNO
# =========================
st.markdown("""
<style>
:root {
    --bg: #0e0e11;
    --card-bg: #16161d;
    --muted: #9ca3af;
    --accent: #22c55e;
    --danger: #ef4444;
    --blue: #3b82f6;
}
html, body, [data-testid="stApp"] { background-color: var(--bg); }
.block-container { padding: 2rem; max-width: 1400px; }
h1 { font-weight: 700; letter-spacing: 0.5px; color:white;}
h2, h3 { font-weight: 600; color:white;}
.quote-card {
    background: linear-gradient(135deg, #1b1b24, #16161d);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #1f1f2b;
    margin-bottom: 1.5rem;
    font-size: 1.6rem;
    color: #9ca3af;
    font-style: italic;
    text-align: center;
}
.metric-card {
    background: linear-gradient(145deg, #1b1b24, #16161d);
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    color: white;
    font-weight: 600;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin-top: 8px;
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
# FUNÇÕES AUXILIARES
# =========================
def limpar_valor(v):
    if pd.isna(v): return 0.0
    if isinstance(v, str):
        v = v.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try: return float(v)
        except: return 0.0
    if isinstance(v, (int,float)): return float(v)
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
with c1:
    st.markdown('<div class="metric-card">💵 Receita Total<div class="metric-value">'+formato_real(receitas["VALOR"].sum())+'</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card">💸 Despesa Total<div class="metric-value">'+formato_real(despesas["VALOR"].sum())+'</div></div>', unsafe_allow_html=True)
with c3:
    saldo_geral = receitas["VALOR"].sum()-despesas["VALOR"].sum()
    cor_saldo = "#3b82f6" if saldo_geral>=0 else "#ef4444"
    st.markdown(f'<div class="metric-card">⚖️ Saldo Geral<div class="metric-value" style="color:{cor_saldo}">{formato_real(saldo_geral)}</div></div>', unsafe_allow_html=True)
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
resumo["MES_ANO_DISPLAY"] = ["📅 "+m.upper() for m in resumo["MES_ANO"]]

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
        if mes > 12: mes -= 12; ano +=1
        meses_a_mostrar.append((ano, mes))
    resumo_plot = resumo[resumo.apply(lambda x: (x["ANO"], x["MES_NUM"]) in meses_a_mostrar, axis=1)].copy()
if resumo_plot.empty: resumo_plot = resumo.copy()

st.subheader("📊 Balanço Financeiro")
fig = px.bar(resumo_plot, x="MES_ANO", y=["RECEITA","DESPESA","SALDO"], barmode="group", text_auto=True)
fig.update_layout(height=420, margin=dict(l=20,r=20,t=40,b=20), legend_title=None)
fig.update_traces(texttemplate="R$ %{y:,.2f}", textposition="inside")
fig.update_traces(selector=dict(name="RECEITA"), marker_color="#22c55e")
fig.update_traces(selector=dict(name="DESPESA"), marker_color="#ef4444")
fig.update_traces(selector=dict(name="SALDO"), marker_color="#3b82f6")
st.plotly_chart(fig, use_container_width=True)

# =========================
# SELECT SLIDER HORIZONTAL PARA MÊS
# =========================
idx_atual = 0
for i, m in enumerate(resumo["MES_ANO_DISPLAY"]):
    if m.startswith("📅 "+hoje.strftime("%b").upper()):
        idx_atual = i
        break
mes_sel_display = st.select_slider("📆 Escolha o mês", options=resumo["MES_ANO_DISPLAY"], value=resumo["MES_ANO_DISPLAY"][idx_atual])
mes_sel = mes_sel_display.replace("📅 ","").lower()
mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

# =========================
# DETALHAMENTO DO MÊS
# =========================
st.subheader(f"📆 Detalhamento — {mes_sel_display}")

rec_mes = receitas[(receitas["ANO"]==ano_sel)&(receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel)&(despesas["MES"]==mes_txt)]

# Cards métricas com indicador de saldo
d1, d2, d3 = st.columns(3)
with d1: st.markdown(f'<div class="metric-card">💰 Receitas<div class="metric-value">{formato_real(rec_mes["VALOR"].sum())}</div></div>', unsafe_allow_html=True)
with d2: st.markdown(f'<div class="metric-card">💸 Despesas<div class="metric-value">{formato_real(des_mes["VALOR"].sum())}</div></div>', unsafe_allow_html=True)
saldo_mes = rec_mes["VALOR"].sum()-des_mes["VALOR"].sum()
cor_saldo = "#3b82f6" if saldo_mes>=0 else "#ef4444"
with d3: st.markdown(f'<div class="metric-card">⚖️ Saldo<div class="metric-value" style="color:{cor_saldo}">{formato_real(saldo_mes)}</div></div>', unsafe_allow_html=True)

# =========================
# COMPOSIÇÃO DO MÊS (BARRAS PERCENTUAIS)
# =========================
st.subheader("📌 Composição do mês (Percentual)")

if not rec_mes.empty:
    rec_mes["PERCENT"] = rec_mes["VALOR"]/rec_mes["VALOR"].sum()*100
    fig_r = px.bar(rec_mes, x="DESCRICAO", y="PERCENT", text="VALOR", color="DESCRICAO", color_discrete_sequence=gerar_cores(len(rec_mes)))
    fig_r.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
    fig_r.update_layout(showlegend=False, yaxis_title="Percentual (%)", margin=dict(t=40,b=40,l=20,r=20))
    st.plotly_chart(fig_r, use_container_width=True)

if not des_mes.empty:
    des_mes["PERCENT"] = des_mes["VALOR"]/des_mes["VALOR"].sum()*100
    fig_d = px.bar(des_mes, x="DESCRICAO", y="PERCENT", text="VALOR", color="DESCRICAO", color_discrete_sequence=gerar_cores(len(des_mes)))
    fig_d.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
    fig_d.update_layout(showlegend=False, yaxis_title="Percentual (%)", margin=dict(t=40,b=40,l=20,r=20))
    st.plotly_chart(fig_d, use_container_width=True)

# =========================
# SALDO ACUMULADO
# =========================
st.subheader("📈 Saldo acumulado")

resumo["SALDO_ACUM"] = resumo["SALDO"].cumsum()
fig_saldo = go.Figure()
fig_saldo.add_trace(go.Scatter(x=resumo["MES_ANO"].str.upper(), y=resumo["SALDO_ACUM"], mode='lines+markers', line=dict(color="#3b82f6", width=3), name="Saldo Acumulado"))
fig_saldo.update_layout(height=400, margin=dict(l=20,r=20,t=40,b=20))
st.plotly_chart(fig_saldo, use_container_width=True)
