import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random
import unicodedata
import time

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Atlas Financeiro",
    page_icon="🌙",
    layout="wide"
)

# =========================
# FRASES
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Consistência vence motivação.",
    "Pequenos passos geram grandes resultados.",
    "Você está construindo algo grande.",
    "Cada número conta uma escolha.",
    "O futuro gosta de quem se organiza no presente."
]

# =========================
# PLANILHA
# =========================
PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

# =========================
# CONTROLE DE ATUALIZAÇÃO
# =========================
if "refresh_key" not in st.session_state:
    st.session_state.refresh_key = str(time.time())

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
:root{
    --bg:#06080d;
    --bg-2:#0b1018;
    --bg-3:#121826;
    --card:rgba(15,20,31,.78);
    --card-2:rgba(18,24,36,.88);
    --stroke:rgba(255,255,255,.08);
    --stroke-2:rgba(255,255,255,.13);
    --text:#edf2f7;
    --muted:#9aa8bc;
    --blue:#6ea8ff;
    --green:#72e0b5;
    --red:#ff8c8c;
    --purple:#b497ff;
    --yellow:#ffd36a;
    --shadow:0 14px 35px rgba(0,0,0,.28);
    --radius:22px;
}
.stApp{
    background:
        radial-gradient(circle at 12% 0%, rgba(110,168,255,.12), transparent 25%),
        radial-gradient(circle at 100% 0%, rgba(180,151,255,.10), transparent 22%),
        linear-gradient(180deg, #05070c 0%, #0a0f17 100%);
    color:var(--text);
}
.block-container{
    max-width:1480px;
    padding-top:1.2rem !important;
    padding-bottom:1.5rem !important;
}
.hero{
    position:relative;
    overflow:hidden;
    padding:24px 24px 18px 24px;
    border:1px solid var(--stroke);
    border-radius:28px;
    background:
        linear-gradient(135deg, rgba(18,24,36,.92) 0%, rgba(10,14,22,.96) 100%);
    box-shadow:var(--shadow);
    margin-bottom:12px;
}
.hero:before{
    content:"";
    position:absolute;
    inset:auto -80px -80px auto;
    width:220px;
    height:220px;
    background:radial-gradient(circle, rgba(110,168,255,.18), transparent 65%);
    pointer-events:none;
}
.hero:after{
    content:"";
    position:absolute;
    inset:-70px auto auto -70px;
    width:190px;
    height:190px;
    background:radial-gradient(circle, rgba(180,151,255,.14), transparent 65%);
    pointer-events:none;
}
.hero-top{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    gap:18px;
    flex-wrap:wrap;
}
.hero-badge{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:7px 12px;
    border-radius:999px;
    background:rgba(255,255,255,.05);
    border:1px solid rgba(255,255,255,.08);
    color:#d8e3f2;
    font-size:.82rem;
    margin-bottom:10px;
}
.hero-title{
    font-size:2.15rem;
    font-weight:800;
    letter-spacing:-.04em;
    line-height:1.1;
    margin:0;
}
.hero-sub{
    color:var(--muted);
    font-size:1rem;
    margin-top:6px;
}
.hero-quote{
    color:#d7e1ef;
    font-size:.92rem;
    padding:12px 14px;
    border-radius:18px;
    background:rgba(255,255,255,.04);
    border:1px solid rgba(255,255,255,.06);
    min-width:260px;
    max-width:420px;
}
.section-card{
    background:linear-gradient(180deg, rgba(15,20,31,.78), rgba(11,15,23,.86));
    border:1px solid var(--stroke);
    border-radius:24px;
    padding:16px 16px 10px 16px;
    box-shadow:var(--shadow);
}
.section-title{
    font-size:1.05rem;
    font-weight:700;
    letter-spacing:-.02em;
    margin-bottom:4px;
}
.section-sub{
    color:var(--muted);
    font-size:.92rem;
    margin-bottom:8px;
}
div[data-testid="stMetric"]{
    background:linear-gradient(180deg, rgba(17,23,35,.94) 0%, rgba(10,14,22,.98) 100%);
    border:1px solid var(--stroke);
    box-shadow:var(--shadow);
    border-radius:22px;
    padding:14px 12px 12px 12px;
    min-height:96px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    transition:all .18s ease;
}
div[data-testid="stMetric"]:hover{
    transform:translateY(-2px);
    border-color:rgba(255,255,255,.15);
}
div[data-testid="stMetricLabel"]{
    font-size:.83rem !important;
    color:var(--muted) !important;
    text-align:center !important;
    justify-content:center !important;
}
div[data-testid="stMetricLabel"] p{
    margin:0 !important;
    line-height:1.08 !important;
    text-align:center !important;
}
div[data-testid="stMetricValue"]{
    font-size:1.20rem !important;
    color:var(--text) !important;
    line-height:1.05 !important;
    text-align:center !important;
    justify-content:center !important;
}
div[data-testid="stMetricValue"] > div{
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:clip !important;
    text-align:center !important;
}
div[data-testid="stMetricDelta"]{
    display:none !important;
}
.stPlotlyChart{
    background:linear-gradient(180deg, rgba(13,17,26,.78), rgba(10,14,21,.88));
    border:1px solid var(--stroke);
    border-radius:22px;
    padding:10px 10px 2px 10px;
    box-shadow:var(--shadow);
}
.stDataFrame{
    border:1px solid var(--stroke) !important;
    border-radius:20px !important;
    overflow:hidden !important;
}
.stSelectbox > div > div,
div[data-baseweb="select"] > div,
div[data-baseweb="base-input"]{
    background:rgba(12,17,26,.9) !important;
    border:1px solid var(--stroke) !important;
    border-radius:16px !important;
    min-height:46px;
}
div.stButton > button{
    min-height:46px;
    border-radius:16px;
    border:1px solid rgba(255,255,255,.10);
    background:linear-gradient(135deg, rgba(110,168,255,.18), rgba(180,151,255,.16));
    color:#eef4ff;
    font-weight:600;
}
div.stButton > button:hover{
    border-color:rgba(255,255,255,.18);
    background:linear-gradient(135deg, rgba(110,168,255,.24), rgba(180,151,255,.22));
}
.soft-note{
    font-size:.92rem;
    color:var(--muted);
    padding:11px 13px;
    border-radius:16px;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.06);
    margin:4px 0 8px 0;
}
hr{
    border-color:rgba(255,255,255,.08) !important;
    margin-top:1rem !important;
    margin-bottom:1rem !important;
}
.small-gap{
    height:6px;
}
</style>
""", unsafe_allow_html=True)

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
        except Exception:
            return 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


def formato_real(v):
    try:
        v = float(v)
    except Exception:
        v = 0.0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def normalizar_texto(txt):
    txt = str(txt).strip().upper()
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", errors="ignore").decode("utf-8")
    return txt


def normalizar_colunas(df):
    df = df.copy()
    df.columns = [normalizar_texto(c) for c in df.columns]
    return df


MESES_PT = {
    1: "JAN", 2: "FEV", 3: "MAR", 4: "ABR", 5: "MAI", 6: "JUN",
    7: "JUL", 8: "AGO", 9: "SET", 10: "OUT", 11: "NOV", 12: "DEZ"
}


def mes_ano_pt(data):
    if pd.isna(data):
        return ""
    return f"{MESES_PT.get(int(data.month), '')}/{data.year}"


def classificar_gasto(valor):
    txt = normalizar_texto(valor)
    if "INDISP" in txt:
        return "INDISPENSAVEL"
    if "DISP" in txt:
        return "DISPENSAVEL"
    return "SEM CLASSIFICACAO"


def preparar_base(base):
    base = normalizar_colunas(base)

    col_data = next((c for c in base.columns if "DATA" in c), None)
    col_valor = next((c for c in base.columns if "VALOR" in c), None)
    col_desc = next((c for c in base.columns if "NOME" in c or "DESCR" in c), None)

    if not col_data or not col_valor or not col_desc:
        return pd.DataFrame(columns=["DATA", "DESCRICAO", "VALOR", "ANO", "MES_NUM", "MES"])

    base = base[[col_data, col_desc, col_valor]].copy()
    base.columns = ["DATA", "DESCRICAO", "VALOR"]

    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce", dayfirst=True)
    base = base.dropna(subset=["DATA"])

    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["MES_NUM"].map(MESES_PT)

    return base


@st.cache_data(show_spinner=False, ttl=60)
def carregar_planilhas(url, refresh_key):
    xls = pd.ExcelFile(url)
    planilhas = {nome: pd.read_excel(xls, sheet_name=nome) for nome in xls.sheet_names}
    return planilhas, xls.sheet_names


def encontrar_aba_gastos(sheet_names):
    nomes_normalizados = {normalizar_texto(nome): nome for nome in sheet_names}
    candidatos = [
        "GASTOS",
        "GASTOS_VARIAVEIS",
        "GASTOS VARIAVEIS",
        "GASTOS EXTRAS",
        "VARIAVEIS",
        "EXTRAS",
    ]
    for cand in candidatos:
        if cand in nomes_normalizados:
            return nomes_normalizados[cand]
    return None


def preparar_gastos(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "DATA", "MES", "QUINZENA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"
        ])

    df = normalizar_colunas(df)

    mapa = {}
    for c in df.columns:
        if "DATA" in c and "DATA" not in mapa.values():
            mapa[c] = "DATA"
        elif (c == "MES" or "MES" in c) and "MES" not in mapa.values():
            mapa[c] = "MES"
        elif "NOME" in c and "NOME" not in mapa.values():
            mapa[c] = "NOME"
        elif "FORMA" in c and "PAG" in c and "FORMA PAGAMENTO" not in mapa.values():
            mapa[c] = "FORMA PAGAMENTO"
        elif "CLASSIFIC" in c and "CLASSIFICACAO" not in mapa.values():
            mapa[c] = "CLASSIFICACAO"
        elif "VALOR" in c and "VALOR" not in mapa.values():
            mapa[c] = "VALOR"

    df = df.rename(columns=mapa)

    obrigatorias = ["DATA", "NOME", "VALOR"]
    if any(col not in df.columns for col in obrigatorias):
        return pd.DataFrame(columns=[
            "DATA", "MES", "QUINZENA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"
        ])

    for col in ["FORMA PAGAMENTO", "CLASSIFICACAO", "MES"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["DATA", "MES", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"]].copy()
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce", dayfirst=True)
    df["VALOR"] = df["VALOR"].apply(limpar_valor)
    df = df.dropna(subset=["DATA"])
    df = df[df["NOME"].astype(str).str.strip() != ""]

    df["CLASSIFICACAO"] = df["CLASSIFICACAO"].apply(classificar_gasto)
    df["FORMA PAGAMENTO"] = (
        df["FORMA PAGAMENTO"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace({"": "NÃO INFORMADO"})
    )

    df["QUINZENA"] = df["DATA"].dt.day.apply(lambda x: "1ª quinzena" if x <= 15 else "2ª quinzena")
    df["ANO"] = df["DATA"].dt.year
    df["MES_NUM"] = df["DATA"].dt.month
    df["MES_ABREV"] = df["MES_NUM"].map(MESES_PT)
    df["MES_ANO"] = df["DATA"].apply(mes_ano_pt)

    mes_limpo = df["MES"].fillna("").astype(str).str.strip().str.upper()
    df["MES"] = mes_limpo.where(mes_limpo != "", df["MES_ABREV"])

    return df.sort_values("DATA", ascending=False)


# =========================
# HERO
# =========================
st.markdown(f"""
<div class="hero">
    <div class="hero-top">
        <div>
            <div class="hero-badge">🌙 Painel financeiro pessoal</div>
            <div class="hero-title">Atlas Financeiro</div>
            <div class="hero-sub">Organização, clareza e visão do todo. Um mapa limpo para o seu dinheiro.</div>
        </div>
        <div class="hero-quote">“{random.choice(FRASES)}”</div>
    </div>
</div>
""", unsafe_allow_html=True)

col_refresh_1, col_refresh_2 = st.columns([1.2, 4.5])
with col_refresh_1:
    if st.button("🔄 Atualizar agora", use_container_width=True):
        st.cache_data.clear()
        st.session_state.refresh_key = str(time.time())
        st.rerun()
with col_refresh_2:
    st.markdown('<div class="soft-note">Lançou algo na planilha e ele não apareceu? Dá um tapa elegante no cache com esse botão.</div>', unsafe_allow_html=True)

# =========================
# LEITURA
# =========================
try:
    planilhas, nomes_abas = carregar_planilhas(PLANILHA_URL, st.session_state.refresh_key)
except Exception as e:
    st.error(f"Erro ao carregar planilha: {e}")
    st.stop()

if not nomes_abas:
    st.error("Nenhuma aba encontrada na planilha.")
    st.stop()

try:
    df = planilhas[nomes_abas[0]].copy()
except Exception as e:
    st.error(f"Erro ao abrir a aba principal: {e}")
    st.stop()

df = normalizar_colunas(df)

meio = len(df.columns) // 2
receitas = preparar_base(df.iloc[:, :meio].copy())
despesas = preparar_base(df.iloc[:, meio:].copy())

# =========================
# RESUMO
# =========================
rec_m = receitas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR": "RECEITA"})
des_m = despesas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR": "DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO", "MES_NUM", "MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO", "MES_NUM"])
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")
resumo["MES_ANO"] = resumo["DATA_CHAVE"].apply(mes_ano_pt)

# =========================
# ANO ATUAL
# =========================
ano_atual = datetime.now().year
mes_atual = datetime.now().month

resumo_ano = resumo[resumo["ANO"] == ano_atual]

total_receita_ano = resumo_ano["RECEITA"].sum()
total_despesa_ano = resumo_ano["DESPESA"].sum()
saldo_ano = resumo_ano["SALDO"].sum()

saldo_restante = resumo_ano[resumo_ano["MES_NUM"] > mes_atual]["SALDO"].sum()

# =========================
# INVESTIMENTO
# =========================
valor_investido = 0.0
for nome_aba in nomes_abas:
    if normalizar_texto(nome_aba) == "INVESTIMENTO":
        try:
            investimento_df = pd.read_excel(PLANILHA_URL, sheet_name=nome_aba, header=None)
            valor_investido = limpar_valor(investimento_df.iloc[13, 1])
        except Exception:
            valor_investido = 0.0
        break

patrimonio_em_construcao = saldo_restante + valor_investido

# =========================
# MÉTRICAS
# =========================
st.markdown('<div class="section-title">Visão do ano</div><div class="section-sub">Os números grandes primeiro. O dinheiro gosta quando a gente olha pra ele sem medo.</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("💵 Receita no Ano", formato_real(total_receita_ano))
c2.metric("💸 Despesa no Ano", formato_real(total_despesa_ano))
c3.metric("🏦 Saldo no Ano", formato_real(saldo_ano))
c4.metric("🧭 Saldo Restante", formato_real(saldo_restante))
c5.metric("📈 Investido", formato_real(valor_investido))
c6.metric("💎 Total em Construção", formato_real(patrimonio_em_construcao))

st.markdown('<div class="small-gap"></div>', unsafe_allow_html=True)

# =========================
# GRÁFICO GERAL
# =========================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 Balanço Financeiro Geral</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Receitas, despesas e saldo mês a mês.</div>', unsafe_allow_html=True)

tema = "plotly_dark" if st.get_option("theme.base") == "dark" else "plotly"
cor_receita = "#6EA8FF"
cor_despesa = "#FF8C8C"
cor_saldo = "#72E0B5"
cor_destaque = "#B497FF"

fig = go.Figure()
fig.add_bar(
    x=resumo["MES_ANO"],
    y=resumo["RECEITA"],
    name="Receita",
    text=resumo["RECEITA"].apply(formato_real),
    textposition="inside",
    textfont=dict(size=11, color="#f8fafc"),
    marker=dict(color=cor_receita, line=dict(width=0)),
    insidetextanchor="middle",
)
fig.add_bar(
    x=resumo["MES_ANO"],
    y=resumo["DESPESA"],
    name="Despesa",
    text=resumo["DESPESA"].apply(formato_real),
    textposition="inside",
    textfont=dict(size=11, color="#f8fafc"),
    marker=dict(color=cor_despesa, line=dict(width=0)),
    insidetextanchor="middle",
)
fig.add_bar(
    x=resumo["MES_ANO"],
    y=resumo["SALDO"],
    name="Saldo",
    text=resumo["SALDO"].apply(formato_real),
    textposition="inside",
    textfont=dict(size=11, color="#081018"),
    marker=dict(color=cor_saldo, line=dict(width=0)),
    insidetextanchor="middle",
)
fig.update_layout(
    template=tema,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    barmode="group",
    bargap=0.24,
    bargroupgap=0.08,
    uniformtext_minsize=8,
    uniformtext_mode="hide",
    height=455,
    margin=dict(l=6, r=6, t=10, b=6),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        bgcolor="rgba(0,0,0,0)"
    ),
    font=dict(color="#e5edf7", size=12),
)
fig.update_xaxes(showgrid=False, tickfont=dict(size=11))
fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# SELECTBOX DINÂMICO (PRÓXIMO MÊS)
# =========================
st.markdown("---")

if mes_atual == 12:
    prox_mes = 1
    prox_ano = ano_atual + 1
else:
    prox_mes = mes_atual + 1
    prox_ano = ano_atual

mes_ref = mes_ano_pt(datetime(prox_ano, prox_mes, 1))
lista_meses = resumo["MES_ANO"].tolist()

if lista_meses:
    idx_default = lista_meses.index(mes_ref) if mes_ref in lista_meses else len(lista_meses) - 1

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📅 Raio-X do mês</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Você escolhe o mês e ele conta a história sem enrolação.</div>', unsafe_allow_html=True)

    mes_sel = st.selectbox("Escolha o mês", lista_meses, index=idx_default)

    mes_txt, ano_sel = mes_sel.split("/")
    ano_sel = int(ano_sel)

    rec_mes = receitas[(receitas["ANO"] == ano_sel) & (receitas["MES"] == mes_txt)]
    des_mes = despesas[(despesas["ANO"] == ano_sel) & (despesas["MES"] == mes_txt)]

    c1, c2, c3 = st.columns(3)
    c1.metric("💵 Receitas", formato_real(rec_mes["VALOR"].sum()))
    c2.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
    c3.metric("🏦 Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

    st.markdown('<div class="small-gap"></div>', unsafe_allow_html=True)
    st.markdown("#### 💸 Despesas do mês selecionado")

    if not des_mes.empty:
        despesas_total = (
            des_mes.groupby("DESCRICAO", as_index=False)["VALOR"]
            .sum()
            .sort_values("VALOR", ascending=False)
            .head(12)
        )

        fig2 = go.Figure(go.Bar(
            x=despesas_total["DESCRICAO"],
            y=despesas_total["VALOR"],
            text=despesas_total["VALOR"].apply(formato_real),
            textposition="inside",
            textfont=dict(size=11, color="#081018"),
            insidetextanchor="middle",
            marker=dict(color=cor_destaque, line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
        ))
        fig2.update_layout(
            template=tema,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=320,
            margin=dict(l=6, r=6, t=8, b=6),
            xaxis_title="",
            yaxis_title="",
            uniformtext_minsize=8,
            uniformtext_mode="hide",
            font=dict(color="#e5edf7", size=12),
        )
        fig2.update_xaxes(showgrid=False)
        fig2.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem despesas neste mês.")

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Não encontrei meses válidos na base principal.")

# =========================
# GASTOS VARIÁVEIS
# =========================
st.markdown("---")
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🧾 Gastos variáveis</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">O que escapa dos gastos fixos aparece aqui.</div>', unsafe_allow_html=True)

aba_gastos = encontrar_aba_gastos(nomes_abas)

if not aba_gastos:
    st.info("Não encontrei uma aba de gastos variáveis. Crie uma aba como GASTOS e use colunas como DATA, MÊS, NOME, FORMA PAGAMENTO, CLASSIFICAÇÃO e VALOR.")
else:
    gastos_raw = planilhas.get(aba_gastos, pd.DataFrame())
    gastos = preparar_gastos(gastos_raw)

    if gastos.empty:
        st.warning(f"Encontrei a aba '{aba_gastos}', mas não consegui montar a base de gastos. Confere se ela tem pelo menos DATA, NOME e VALOR.")
    else:
        meses_gastos = sorted(gastos["MES_ANO"].dropna().unique().tolist(), reverse=True)
        mes_padrao = mes_ano_pt(datetime.now())
        idx_mes_gasto = meses_gastos.index(mes_padrao) if mes_padrao in meses_gastos else 0

        colf1, colf2, colf3 = st.columns([1.5, 1, 1.2])
        with colf1:
            mes_gasto_sel = st.selectbox("📅 Mês dos gastos", meses_gastos, index=idx_mes_gasto)
        with colf2:
            quinzena_sel = st.selectbox("🗓️ Quinzena", ["Todas", "1ª quinzena", "2ª quinzena"], index=0)
        with colf3:
            classif_sel = st.selectbox("Filtro", ["Todos", "Indispensável 👍", "Dispensável 👎"], index=0)

        st.markdown(
            '<div class="soft-note">👍 indispensável = necessário • 👎 dispensável = dá pra segurar</div>',
            unsafe_allow_html=True,
        )

        gastos_filt = gastos[gastos["MES_ANO"] == mes_gasto_sel].copy()

        if quinzena_sel != "Todas":
            gastos_filt = gastos_filt[gastos_filt["QUINZENA"] == quinzena_sel].copy()

        if classif_sel == "Indispensável 👍":
            gastos_filt = gastos_filt[gastos_filt["CLASSIFICACAO"] == "INDISPENSAVEL"].copy()
        elif classif_sel == "Dispensável 👎":
            gastos_filt = gastos_filt[gastos_filt["CLASSIFICACAO"] == "DISPENSAVEL"].copy()

        total_gastos = gastos_filt["VALOR"].sum()
        qtd_lanc = len(gastos_filt)
        total_indisp = gastos_filt.loc[
            gastos_filt["CLASSIFICACAO"].astype(str).str.upper() == "INDISPENSAVEL", "VALOR"
        ].sum()
        total_disp = gastos_filt.loc[
            gastos_filt["CLASSIFICACAO"].astype(str).str.upper() == "DISPENSAVEL", "VALOR"
        ].sum()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💸 Total no período", formato_real(total_gastos))
        m2.metric("🧾 Lançamentos", str(qtd_lanc))
        m3.metric("👍 Indispensável", formato_real(total_indisp))
        m4.metric("👎 Dispensável", formato_real(total_disp))

        gc1, gc2 = st.columns([1, 1.45])

        with gc1:
            st.markdown("#### 📊 Gastos por classificação")
            if gastos_filt.empty:
                st.info("Sem gastos nesse filtro.")
            else:
                classif = gastos_filt.copy()
                classif["CLASSIFICACAO_LABEL"] = classif["CLASSIFICACAO"].replace({
                    "INDISPENSAVEL": "👍 Indispensável",
                    "DISPENSAVEL": "👎 Dispensável",
                    "SEM CLASSIFICACAO": "Sem classificação",
                })
                graf_class = (
                    classif.groupby("CLASSIFICACAO_LABEL", as_index=False)["VALOR"]
                    .sum()
                    .sort_values("VALOR", ascending=False)
                )

                cores_classificacao = []
                for item in graf_class["CLASSIFICACAO_LABEL"]:
                    if "Indispensável" in item:
                        cores_classificacao.append("#72E0B5")
                    elif "Dispensável" in item:
                        cores_classificacao.append("#FF9B9B")
                    else:
                        cores_classificacao.append("#8CB9FF")

                fig3 = go.Figure(go.Bar(
                    x=graf_class["CLASSIFICACAO_LABEL"],
                    y=graf_class["VALOR"],
                    text=graf_class["VALOR"].apply(formato_real),
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(size=13, color="#081018"),
                    marker=dict(color=cores_classificacao, line=dict(width=0)),
                    hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
                ))
                fig3.update_layout(
                    template=tema,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=340,
                    margin=dict(l=12, r=12, t=8, b=6),
                    xaxis_title="",
                    yaxis_title="",
                    uniformtext_minsize=10,
                    uniformtext_mode="hide",
                    font=dict(color="#e5edf7", size=12),
                )
                fig3.update_xaxes(showgrid=False)
                fig3.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
                st.plotly_chart(fig3, use_container_width=True)

        with gc2:
            st.markdown("#### 🧩 Seus gastos item por item")
            if gastos_filt.empty:
                st.info("Sem gastos nesse filtro.")
            else:
                graf_itens = (
                    gastos_filt.groupby("NOME", as_index=False)["VALOR"]
                    .sum()
                    .sort_values("VALOR", ascending=False)
                    .head(12)
                )

                fig4 = go.Figure(go.Bar(
                    x=graf_itens["NOME"],
                    y=graf_itens["VALOR"],
                    text=graf_itens["VALOR"].apply(formato_real),
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont=dict(size=12, color="#f8fafc"),
                    marker=dict(color=cor_receita, line=dict(width=0)),
                    hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
                ))
                fig4.update_layout(
                    template=tema,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=340,
                    margin=dict(l=12, r=12, t=8, b=6),
                    xaxis_title="",
                    yaxis_title="",
                    uniformtext_minsize=9,
                    uniformtext_mode="hide",
                    font=dict(color="#e5edf7", size=12),
                )
                fig4.update_xaxes(showgrid=False)
                fig4.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
                st.plotly_chart(fig4, use_container_width=True)

        st.markdown("#### 📋 Tabela de gastos")
        tabela_gastos = gastos_filt.copy()
        tabela_gastos["DATA"] = tabela_gastos["DATA"].dt.strftime("%d/%m/%Y")
        tabela_gastos["CLASSIFICACAO"] = tabela_gastos["CLASSIFICACAO"].replace({
            "INDISPENSAVEL": "👍 Indispensável",
            "DISPENSAVEL": "👎 Dispensável",
            "SEM CLASSIFICACAO": "Sem classificação",
        })
        tabela_gastos["VALOR_FMT"] = tabela_gastos["VALOR"].map(formato_real)
        tabela_gastos = tabela_gastos.rename(columns={
            "DATA": "Data",
            "MES": "Mês",
            "QUINZENA": "Quinzena",
            "NOME": "Nome",
            "FORMA PAGAMENTO": "Forma pagamento",
            "CLASSIFICACAO": "Classificação",
        })

        st.dataframe(
            tabela_gastos[[
                "Data", "Mês", "Quinzena", "Nome", "Forma pagamento", "Classificação", "VALOR_FMT"
            ]].rename(columns={"VALOR_FMT": "Valor"}),
            use_container_width=True,
            hide_index=True,
        )

st.markdown('</div>', unsafe_allow_html=True)
