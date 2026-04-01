import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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
  --bg:#06070a;
  --bg-page:#06070a;
  --bg-elev:#0b0f14;
  --bg-card:#0f141b;
  --bg-card-soft:#111821;
  --bg-card-2:#151d27;
  --border-soft:#1f2937;
  --border-strong:#2d3a4b;
  --accent:#22c55e;
  --accent-soft:#2dd4bf;
  --accent-blue:#60a5fa;
  --accent-warm:#f59e0b;
  --text:#eef2f7;
  --muted:#94a3b8;
  --danger:#f87171;
  --purple:#a78bfa;
  --yellow:#fbbf24;
  --shadow:0 18px 45px rgba(0,0,0,.30);
}
html, body, [class*="css"] {
  background:
    radial-gradient(circle at top left, rgba(45,212,191,.08), transparent 26%),
    radial-gradient(circle at top right, rgba(96,165,250,.08), transparent 24%),
    linear-gradient(180deg, #050608 0%, #080b10 100%) !important;
  color: var(--text) !important;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stSidebar"],
section[data-testid="stSidebar"],
.main, main {
  background-color: #06070a !important;
  color: var(--text) !important;
}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(circle at top left, rgba(45,212,191,.08), transparent 26%),
    radial-gradient(circle at top right, rgba(96,165,250,.08), transparent 24%),
    linear-gradient(180deg, #050608 0%, #080b10 100%) !important;
  padding-top: .7rem !important;
}
.stApp { background: transparent !important; }
[data-testid="stHeader"]{ background: transparent !important; height:0 !important; min-height:0 !important; visibility:hidden !important; }
[data-testid="stToolbar"]{ background: transparent !important; right:10px !important; top:10px !important; }
[data-testid="stDecoration"]{ display:none !important; }
label, p, span, div, h1, h2, h3, h4, h5, h6, small { color: inherit; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
.stCaption,
label,
.stSelectbox label,
.stTextInput label,
.stMultiSelect label { color: var(--text) !important; }
.block-container{
  max-width: 1540px !important;
  padding-top: .3rem !important;
  padding-right: 1rem !important;
  padding-left: 1rem !important;
  padding-bottom: 1.8rem !important;
}
.topbar{
  position: sticky; top: 10px; z-index: 30; display:flex; align-items:center; justify-content:space-between;
  gap:18px; padding:16px 20px; margin: 0 0 16px 0 !important; border-radius:24px;
  background: linear-gradient(90deg, rgba(8,13,20,.94) 0%, rgba(8,17,30,.92) 52%, rgba(8,13,20,.94) 100%);
  border:1px solid rgba(96,165,250,.14); box-shadow:0 10px 30px rgba(0,0,0,.32), inset 0 1px 0 rgba(255,255,255,.03);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); overflow: hidden;
}
.topbar::before{ content:""; position:absolute; inset:0; background: linear-gradient(120deg, rgba(34,211,238,.05), transparent 22%, transparent 78%, rgba(96,165,250,.05)), radial-gradient(circle at top left, rgba(45,212,191,.10), transparent 24%); pointer-events:none; }
.topbar > *{ position:relative; z-index:1; }
.topbar-left{display:flex;align-items:center;gap:14px;min-width:0;}
.logo-pill{ width:56px;height:56px;border-radius:18px; background:linear-gradient(180deg, #12213e 0%, #0f172a 100%); border:1px solid rgba(96,165,250,.22); box-shadow: inset 0 1px 0 rgba(255,255,255,.04); display:flex;align-items:center;justify-content:center; color:white;font-weight:900;font-size:22px; }
.top-kicker{ font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:var(--accent-soft); margin-bottom:3px; font-weight:700; }
.top-title{ font-size:24px; font-weight:800; letter-spacing:-0.04em; line-height:1.05; }
.top-subtitle{ font-size:12px; color:var(--muted); margin-top:4px; }
.top-right-badge { display:flex; flex-wrap:wrap; justify-content:flex-end; gap:8px; }
.top-chip { padding:8px 12px; border-radius:999px; border:1px solid rgba(148,163,184,.14); background:rgba(255,255,255,.03); color:#dbe5f2; font-size:11px; backdrop-filter: blur(10px); }
.top-chip span { color:var(--accent-soft); font-weight:700; }
.control-row{ display:flex; gap:10px; align-items:stretch; flex-wrap:wrap; margin-bottom: 12px; }
.premium-note{ flex: 1 1 340px; padding:12px 14px; border-radius:18px; background:linear-gradient(180deg, rgba(15,20,27,.94), rgba(11,16,23,.94)); border:1px solid rgba(148,163,184,.12); color:var(--muted); box-shadow:0 12px 28px rgba(0,0,0,.18); }
.section-head{ margin: 12px 0 8px 0; }
.section-title{ font-size:18px; font-weight:800; letter-spacing:-.02em; color:#eef3fb; margin-bottom:2px; }
.section-sub{ color:#9aa8bc; font-size:12px; margin-bottom:8px; line-height:1.45; }
.kpi-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
.kpi-card { flex:1 1 180px; min-width:0; padding:16px 16px; border-radius:20px; background:linear-gradient(180deg, rgba(17,24,33,.96), rgba(12,17,24,.96)); border:1px solid rgba(148,163,184,.12); box-shadow:0 12px 28px rgba(0,0,0,.20); position:relative; overflow:hidden; transition:transform .14s ease, border-color .14s ease, box-shadow .14s ease; }
.kpi-card::before{ content:""; position:absolute; inset:0 0 auto 0; height:3px; background:linear-gradient(90deg, var(--accent-soft), var(--accent-blue)); opacity:.95; }
.kpi-card:hover{ transform:translateY(-2px); border-color:rgba(96,165,250,.24); box-shadow:0 18px 34px rgba(0,0,0,.24); }
.kpi-label { font-size:10px; text-transform:uppercase; letter-spacing:0.18em; color:var(--muted); margin-bottom:7px; font-weight:700; }
.kpi-value { font-size:24px; font-weight:800; letter-spacing:-0.03em; }
.kpi-pill { font-size:11px; color:var(--muted); margin-top:6px; line-height:1.35; }
div[role="radiogroup"]{ gap:8px !important; background:rgba(9,12,17,.82); border:1px solid rgba(148,163,184,.12); border-radius:18px; padding:8px; margin: 2px 0 16px 0; box-shadow:0 8px 24px rgba(0,0,0,.20); }
div[role="radiogroup"] > label { margin:0 !important; background:transparent; border:1px solid transparent; border-radius:14px; padding:8px 14px !important; transition:all .16s ease; }
div[role="radiogroup"] > label:hover { background:rgba(255,255,255,.035); border-color:rgba(148,163,184,.14); }
div[role="radiogroup"] > label p { color:#cbd5e1 !important; font-weight:600; font-size:13px !important; }
div[role="radiogroup"] > label:has(input:checked) { background:linear-gradient(135deg, rgba(45,212,191,.16), rgba(96,165,250,.13)); border-color:rgba(45,212,191,.28); box-shadow: inset 0 1px 0 rgba(255,255,255,.04); }
div[role="radiogroup"] > label:has(input:checked) p { color:white !important; }
.stPlotlyChart, .stDataFrame, div[data-testid="stMetric"]{ border:1px solid rgba(148,163,184,.12) !important; border-radius:20px !important; box-shadow:0 12px 28px rgba(0,0,0,.18) !important; }
.stPlotlyChart{ background:linear-gradient(180deg, rgba(13,17,26,.78), rgba(10,14,21,.88)) !important; padding:10px 10px 2px 10px !important; }
.stDataFrame{ overflow:hidden !important; }
.stDataFrame thead tr th { background:#0f172a !important; color:#e5e7eb !important; font-size:11px !important; text-transform:uppercase; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, [data-testid="stTextInputRootElement"] > div, [data-testid="stNumberInputRootElement"] > div, [data-testid="stSelectbox"] > div, [data-testid="stMultiSelect"] > div, div[data-baseweb="base-input"]{ background: #0c1117 !important; color: var(--text) !important; border-color: rgba(148,163,184,.18) !important; border-radius:16px !important; min-height:50px !important; }
.stButton > button{ border-radius:16px !important; border:1px solid rgba(148,163,184,.14) !important; background:linear-gradient(180deg, #111821, #0d131b) !important; color:#edf2f7 !important; font-weight:700 !important; padding:.72rem .95rem !important; min-height:50px !important; }
.stButton > button:hover{ border-color:rgba(45,212,191,.28) !important; transform:translateY(-1px); }
div[data-testid="stMetric"]{ background:linear-gradient(180deg, rgba(17,23,35,.96) 0%, rgba(10,14,22,.99) 100%) !important; min-height:102px; display:flex; align-items:center; justify-content:center; text-align:center; transition:all .18s ease; }
div[data-testid="stMetric"]:hover{ transform:translateY(-2px); border-color:rgba(255,255,255,.14) !important; }
div[data-testid="stMetricLabel"]{ font-size:.88rem !important; color:#98a6ba !important; text-align:center !important; justify-content:center !important; }
div[data-testid="stMetricLabel"] p{ margin:0 !important; line-height:1.1 !important; text-align:center !important; }
div[data-testid="stMetricValue"]{ font-size:1.42rem !important; font-weight:800 !important; color:#f3f7ff !important; line-height:1.08 !important; text-align:center !important; justify-content:center !important; }
div[data-testid="stMetricValue"] > div{ white-space:normal !important; overflow:visible !important; text-overflow:clip !important; text-align:center !important; }
div[data-testid="stMetricDelta"]{ display:none !important; }
.soft-note{ font-size:.92rem; color:var(--muted); padding:11px 13px; border-radius:16px; background:rgba(255,255,255,.035); border:1px solid rgba(255,255,255,.06); margin:6px 0 10px 0; }
.small-gap{ height:6px; }
hr { border:none !important; height:1px !important; background:linear-gradient(90deg, transparent, rgba(148,163,184,.18), transparent) !important; margin:.95rem 0 !important; }
@media (max-width: 900px){ .block-container{padding-left:.7rem !important;padding-right:.7rem !important;} .topbar{flex-direction:column;align-items:flex-start;} .top-right-badge{justify-content:flex-start;} .top-title{font-size:20px;} .kpi-value{font-size:21px;} }
@media (max-width: 768px){ .topbar{ top:8px; flex-direction:column; align-items:flex-start; gap:10px; padding:14px 14px; border-radius:18px; } .top-right-badge{ width:100%; justify-content:flex-start; gap:6px; } .top-chip{ padding:7px 12px; font-size:11px; } .logo-pill{ width:46px; height:46px; border-radius:14px; font-size:20px; } .top-title{ font-size:18px; line-height:1.12; } .top-subtitle{ font-size:11px; line-height:1.3; } .kpi-card{ padding:13px 14px; border-radius:16px; } .kpi-value{ font-size:18px; } }
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




def render_topbar():
    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-left">
        <div class="logo-pill">AF</div>
        <div>
          <div class="top-kicker">Dashboard financeiro premium</div>
          <div class="top-title">Atlas Financeiro</div>
          <div class="top-subtitle">Organização, clareza e visão do todo. Um painel mais limpo, firme e elegante para o seu dinheiro.</div>
        </div>
      </div>
      <div class="top-right-badge">
        <div class="top-chip">🌙 Visual <span>dark premium</span></div>
        <div class="top-chip">📊 Base <span>Google Sheets</span></div>
        <div class="top-chip">✨ Frase do dia <span>{random.choice(FRASES)}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(cards):
    html = '<div class="kpi-row">'
    for card in cards:
        label = card.get('label', '')
        value = card.get('value', '')
        hint = card.get('hint', '')
        html += f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-pill">{hint}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# =========================
# HERO PREMIUM
# =========================
render_topbar()

col_refresh_1, col_refresh_2 = st.columns([1.2, 4.8])
with col_refresh_1:
    if st.button("🔄 Atualizar agora", use_container_width=True):
        st.cache_data.clear()
        st.session_state.refresh_key = str(time.time())
        st.rerun()
with col_refresh_2:
    st.markdown(
        '<div class="premium-note">Mesmo motor, agora com acabamento de app caro: layout mais firme, respiro melhor e leitura mais gostosa. Se a planilha mudou, esse botão puxa a cena de volta pro presente.</div>',
        unsafe_allow_html=True
    )

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



def format_pct(v):
    try:
        return f"{float(v):.1f}%".replace(".", ",")
    except Exception:
        return "0,0%"


def faixa_percentual(p):
    try:
        p = float(p)
    except Exception:
        return "—"
    if p <= 5:
        return "Leve"
    elif p <= 15:
        return "Controlado"
    elif p <= 30:
        return "Pesa"
    return "Muito pesado"


def analise_subcategoria(pct_renda, categoria=""):
    try:
        p = float(pct_renda)
    except Exception:
        p = 0.0

    if p <= 2:
        return "Impacto bem pequeno na renda. Dá para manter sem drama."
    elif p <= 5:
        return "Impacto leve. Bom ponto para pequenos ajustes finos."
    elif p <= 10:
        return "Já aparece no orçamento. Vale acompanhar para não crescer no escuro."
    elif p <= 20:
        return "Peso relevante. Se apertar, aqui já existe espaço para revisar."
    elif p <= 30:
        return "Peso alto na renda. Merece atenção real e comparação de alternativas."
    else:
        if normalizar_texto(categoria) == "MORADIA":
            return "Muito pesado para a renda. Moradia virou o centro do tabuleiro."
        return "Muito pesado para a renda. Este item domina o orçamento e pede revisão."


def parse_money_excel(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if not s:
        return 0.0
    s = s.replace("R$", "").replace("r$", "").replace(" ", "")
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def encontrar_aba_custo_vida(sheet_names):
    nomes_normalizados = {normalizar_texto(nome): nome for nome in sheet_names}
    candidatos = [
        "CUSTO DE VIDA",
        "CUSTO_DE_VIDA",
        "CUSTO VIDA",
        "PLANEJAMENTO DE CUSTO DE VIDA",
    ]
    for cand in candidatos:
        if cand in nomes_normalizados:
            return nomes_normalizados[cand]
    return None


@st.cache_data(show_spinner=False, ttl=60)
def carregar_custo_vida_raw(url, nome_aba, refresh_key):
    return pd.read_excel(url, sheet_name=nome_aba, header=None)


def extrair_projeto_morar_sozinho(df_raw):
    renda_total = 0.0
    custos_totais = 0.0
    sobra_mes = 0.0
    categoria_atual = None
    itens = []

    categorias_validas = {"RENDA", "MORADIA", "ALIMENTACAO", "ALIMENTAÇÃO", "TRANSPORTE", "OUTROS"}

    for _, row in df_raw.iterrows():
        a = str(row.iloc[0]).strip() if len(row) > 0 and pd.notna(row.iloc[0]) else ""
        b = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""
        c = row.iloc[2] if len(row) > 2 else None

        a_up = normalizar_texto(a)
        b_up = normalizar_texto(b)
        valor = parse_money_excel(c)

        if "RENDA TOTAL" in a_up:
            renda_total = valor
            continue
        if "CUSTOS TOTAIS" in a_up:
            custos_totais = valor
            continue
        if "SOBRA NO MES" in a_up:
            sobra_mes = valor
            continue

        if a_up == "CATEGORIA" and b_up in {"DESCRICAO", "DESCRICAO"}:
            continue

        if a_up in categorias_validas:
            categoria_atual = "ALIMENTAÇÃO" if "ALIMENT" in a_up else a_up
            if b and not b_up.startswith("TOTAL"):
                itens.append({
                    "CATEGORIA": categoria_atual,
                    "SUBCATEGORIA": b,
                    "VALOR": valor,
                })
            continue

        if categoria_atual and b and not b_up.startswith("TOTAL"):
            itens.append({
                "CATEGORIA": categoria_atual,
                "SUBCATEGORIA": b,
                "VALOR": valor,
            })

    df_itens = pd.DataFrame(itens)
    if df_itens.empty:
        return {
            "renda_total": renda_total,
            "custos_totais": custos_totais,
            "sobra_mes": sobra_mes,
            "df_itens": pd.DataFrame(columns=["CATEGORIA", "SUBCATEGORIA", "VALOR"]),
            "df_cat": pd.DataFrame(columns=["CATEGORIA", "VALOR"]),
        }

    df_itens["SUBCATEGORIA"] = df_itens["SUBCATEGORIA"].fillna("").astype(str).str.strip()
    df_itens["VALOR"] = df_itens["VALOR"].fillna(0.0).astype(float)
    df_itens = df_itens[df_itens["SUBCATEGORIA"] != ""].copy()

    if renda_total <= 0:
        renda_total = df_itens.loc[df_itens["CATEGORIA"] == "RENDA", "VALOR"].sum()
    if custos_totais <= 0:
        custos_totais = df_itens.loc[df_itens["CATEGORIA"] != "RENDA", "VALOR"].sum()
    if renda_total > 0 and sobra_mes == 0:
        sobra_mes = renda_total - custos_totais

    df_cat = df_itens.groupby("CATEGORIA", as_index=False)["VALOR"].sum()

    mapa_cat = df_cat.set_index("CATEGORIA")["VALOR"].to_dict()
    df_itens["TOTAL_CATEGORIA"] = df_itens["CATEGORIA"].map(mapa_cat).fillna(0.0)

    if renda_total > 0:
        df_itens["PCT_RENDA"] = (df_itens["VALOR"] / renda_total) * 100
        df_cat["PCT_RENDA"] = (df_cat["VALOR"] / renda_total) * 100
        pct_sobra = (sobra_mes / renda_total) * 100
    else:
        df_itens["PCT_RENDA"] = 0.0
        df_cat["PCT_RENDA"] = 0.0
        pct_sobra = 0.0

    df_itens["PCT_CATEGORIA"] = (
        df_itens["VALOR"] / df_itens["TOTAL_CATEGORIA"].replace(0, pd.NA) * 100
    ).fillna(0.0)

    df_itens["VALOR_FMT"] = df_itens["VALOR"].apply(formato_real)
    df_itens["PCT_RENDA_FMT"] = df_itens["PCT_RENDA"].apply(format_pct)
    df_itens["PCT_CATEGORIA_FMT"] = df_itens["PCT_CATEGORIA"].apply(format_pct)
    df_itens["FAIXA"] = df_itens["PCT_RENDA"].apply(faixa_percentual)
    df_itens["ANALISE"] = df_itens.apply(
        lambda r: analise_subcategoria(r["PCT_RENDA"], r["CATEGORIA"]),
        axis=1
    )

    df_cat["VALOR_FMT"] = df_cat["VALOR"].apply(formato_real)
    df_cat["PCT_RENDA_FMT"] = df_cat["PCT_RENDA"].apply(format_pct)
    df_cat["FAIXA"] = df_cat["PCT_RENDA"].apply(faixa_percentual)

    return {
        "renda_total": renda_total,
        "custos_totais": custos_totais,
        "sobra_mes": sobra_mes,
        "pct_sobra": pct_sobra,
        "df_itens": df_itens,
        "df_cat": df_cat,
    }

# =========================
# TABS
# =========================


# =========================
# NAVEGAÇÃO PREMIUM
# =========================
if "atlas_nav" not in st.session_state:
    st.session_state.atlas_nav = "🌙 Atlas Financeiro"

NAV_OPTS = ["🌙 Atlas Financeiro", "🏠 Projeto Morar Sozinho"]
nav_index = NAV_OPTS.index(st.session_state.atlas_nav) if st.session_state.atlas_nav in NAV_OPTS else 0
st.radio(
    "Navegação",
    options=NAV_OPTS,
    index=nav_index,
    key="atlas_nav",
    horizontal=True,
    label_visibility="collapsed",
)

nav = st.session_state.atlas_nav

if nav == "🌙 Atlas Financeiro":
    # =========================
    # MÉTRICAS
    # =========================
    st.markdown("""
    <div class="section-head">
        <div class="section-title">Visão do ano</div>
        <div class="section-sub">Os números grandes primeiro. Clareza antes de pressa.</div>
    </div>
    """, unsafe_allow_html=True)

    render_kpi_cards([
        {"label": "Receita no ano", "value": formato_real(total_receita_ano), "hint": "Tudo que entrou no ano atual."},
        {"label": "Despesa no ano", "value": formato_real(total_despesa_ano), "hint": "Tudo que saiu no ano atual."},
        {"label": "Saldo no ano", "value": formato_real(saldo_ano), "hint": "Receita menos despesa, sem teatro."},
        {"label": "Saldo restante", "value": formato_real(saldo_restante), "hint": "Projeção do que ainda pode sobrar nos meses à frente."},
        {"label": "Investido", "value": formato_real(valor_investido), "hint": "Valor puxado da aba de investimento."},
        {"label": "Total em construção", "value": formato_real(patrimonio_em_construcao), "hint": "Saldo restante somado ao que já está investido."},
    ])

    st.markdown('<div class="small-gap"></div>', unsafe_allow_html=True)

    # =========================
    # GRÁFICO GERAL
    # =========================
    st.markdown("""
    <div class="section-head">
        <div class="section-title">📊 Balanço Financeiro Geral</div>
        <div class="section-sub">Receitas, despesas e saldo mês a mês.</div>
    </div>
    """, unsafe_allow_html=True)

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

        st.markdown("""
        <div class="section-head">
            <div class="section-title">📅 Raio-X do mês</div>
            <div class="section-sub">Você escolhe o mês e ele conta a história sem enrolação.</div>
        </div>
        """, unsafe_allow_html=True)

        mes_sel = st.selectbox("Escolha o mês", lista_meses, index=idx_default)

        mes_txt, ano_sel = mes_sel.split("/")
        ano_sel = int(ano_sel)

        rec_mes = receitas[(receitas["ANO"] == ano_sel) & (receitas["MES"] == mes_txt)]
        des_mes = despesas[(despesas["ANO"] == ano_sel) & (despesas["MES"] == mes_txt)]

        render_kpi_cards([
            {"label": "Receitas", "value": formato_real(rec_mes["VALOR"].sum()), "hint": f"Entradas do mês {mes_sel}."},
            {"label": "Despesas", "value": formato_real(des_mes["VALOR"].sum()), "hint": f"Saídas do mês {mes_sel}."},
            {"label": "Saldo", "value": formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()), "hint": "O que sobrou depois da poeira baixar."},
        ])

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
    else:
        st.info("Não encontrei meses válidos na base principal.")

    # =========================
    # GASTOS VARIÁVEIS
    # =========================
    st.markdown("---")

    st.markdown("""
    <div class="section-head">
        <div class="section-title">🧾 Gastos variáveis</div>
        <div class="section-sub">O que escapa dos gastos fixos aparece aqui.</div>
    </div>
    """, unsafe_allow_html=True)

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

            render_kpi_cards([
                {"label": "Total no período", "value": formato_real(total_gastos), "hint": "Soma dos gastos no filtro atual."},
                {"label": "Lançamentos", "value": str(qtd_lanc), "hint": "Quantidade de registros encontrados."},
                {"label": "Indispensável", "value": formato_real(total_indisp), "hint": "O pedaço necessário do mês."},
                {"label": "Dispensável", "value": formato_real(total_disp), "hint": "O que dá margem para apertar o freio."},
            ])

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



elif nav == "🏠 Projeto Morar Sozinho":
        st.markdown("""
        <div class="section-head">
            <div class="section-title">🏠 Projeto Morar Sozinho</div>
            <div class="section-sub">Sua aba CUSTO DE VIDA virando mapa de decisão: o que pesa, o que cabe, e onde dá para mexer.</div>
        </div>
        """, unsafe_allow_html=True)

        aba_custo_vida = encontrar_aba_custo_vida(nomes_abas)
        if not aba_custo_vida:
            st.info("Não encontrei a aba 'CUSTO DE VIDA' na planilha.")
        else:
            try:
                raw_cv = carregar_custo_vida_raw(PLANILHA_URL, aba_custo_vida, st.session_state.refresh_key)
                projeto = extrair_projeto_morar_sozinho(raw_cv)

                renda_total = projeto["renda_total"]
                custos_totais = projeto["custos_totais"]
                sobra_mes = projeto["sobra_mes"]
                pct_sobra = projeto["pct_sobra"]
                df_itens = projeto["df_itens"]
                df_cat = projeto["df_cat"]

                if renda_total <= 0 or df_itens.empty:
                    st.warning("Achei a aba, mas não consegui montar o planejamento. Dá uma olhada se a estrutura segue o print que você mostrou.")
                else:
                    reserva_6m = custos_totais * 6
                    pct_custos = (custos_totais / renda_total * 100) if renda_total > 0 else 0

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("💰 Renda total", formato_real(renda_total))
                    m2.metric("💸 Custos totais", f"{formato_real(custos_totais)} • {format_pct(pct_custos)}")
                    m3.metric("🫰 Sobra no mês", f"{formato_real(sobra_mes)} • {format_pct(pct_sobra)}")
                    m4.metric("🛟 Reserva ideal (6 meses)", formato_real(reserva_6m))

                    mapa_cat = df_cat.set_index("CATEGORIA")["VALOR"].to_dict()
                    mapa_pct = df_cat.set_index("CATEGORIA")["PCT_RENDA"].to_dict()

                    moradia_val = mapa_cat.get("MORADIA", 0.0)
                    alimentacao_val = mapa_cat.get("ALIMENTAÇÃO", mapa_cat.get("ALIMENTACAO", 0.0))
                    transporte_val = mapa_cat.get("TRANSPORTE", 0.0)
                    outros_val = mapa_cat.get("OUTROS", 0.0)

                    moradia_pct = mapa_pct.get("MORADIA", 0.0)
                    alimentacao_pct = mapa_pct.get("ALIMENTAÇÃO", mapa_pct.get("ALIMENTACAO", 0.0))
                    transporte_pct = mapa_pct.get("TRANSPORTE", 0.0)
                    outros_pct = mapa_pct.get("OUTROS", 0.0)

                    st.markdown('<div class="small-gap"></div>', unsafe_allow_html=True)
                    st.markdown("#### 📌 Leitura rápida do cenário")
                    st.markdown(
                        f"""
    - **Moradia:** **{formato_real(moradia_val)}** → **{format_pct(moradia_pct)}**
    - **Alimentação:** **{formato_real(alimentacao_val)}** → **{format_pct(alimentacao_pct)}**
    - **Transporte:** **{formato_real(transporte_val)}** → **{format_pct(transporte_pct)}**
    - **Outros:** **{formato_real(outros_val)}** → **{format_pct(outros_pct)}**
    - **Sobra no mês:** **{formato_real(sobra_mes)}** → **{format_pct(pct_sobra)}**
    """
                    )

                    c1, c2 = st.columns([1.1, 1])

                    with c1:
                        st.markdown("#### 📊 Peso das categorias na renda")
                        df_cat_plot = df_cat[df_cat["CATEGORIA"] != "RENDA"].copy()
                        ordem = {"MORADIA": 1, "ALIMENTAÇÃO": 2, "TRANSPORTE": 3, "OUTROS": 4}
                        df_cat_plot["ORDEM"] = df_cat_plot["CATEGORIA"].map(ordem).fillna(99)
                        df_cat_plot = df_cat_plot.sort_values(["ORDEM", "PCT_RENDA"], ascending=[True, False])

                        fig_cat = go.Figure(go.Bar(
                            x=df_cat_plot["CATEGORIA"],
                            y=df_cat_plot["VALOR"],
                            text=df_cat_plot["VALOR_FMT"],
                            textposition="inside",
                            insidetextanchor="middle",
                            textfont=dict(size=13, color="#081018"),
                            marker=dict(
                                color=["#72E0B5", "#FFD36A", "#6EA8FF", "#B497FF"][:len(df_cat_plot)],
                                line=dict(width=0)
                            ),
                            hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
                        ))
                        fig_cat.update_layout(
                            template=tema,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            height=360,
                            margin=dict(l=10, r=10, t=10, b=10),
                            xaxis_title="",
                            yaxis_title="Valor (R$)",
                            uniformtext_minsize=10,
                            uniformtext_mode="hide",
                            font=dict(color="#e5edf7", size=12),
                            showlegend=False,
                        )
                        fig_cat.update_xaxes(showgrid=False)
                        fig_cat.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
                        st.plotly_chart(fig_cat, use_container_width=True)

                    with c2:
                        st.markdown("#### 🧠 Diagnóstico")
                        if pct_sobra >= 30:
                            st.success("Sua sobra está forte. O cenário respira e aceita melhor imprevistos.")
                        elif pct_sobra >= 20:
                            st.info("Seu plano está bom. Já existe folga, mas ainda dá para lapidar.")
                        elif pct_sobra >= 10:
                            st.warning("Dá para ir, mas o orçamento já sente qualquer tropeço.")
                        else:
                            st.error("Sua sobra está curta. Antes de acelerar, vale reduzir custos ou ganhar mais.")

                        top_cat = df_cat[df_cat["CATEGORIA"] != "RENDA"].sort_values("PCT_RENDA", ascending=False).head(3)
                        st.markdown("**Onde o dinheiro pesa mais:**")
                        for _, row in top_cat.iterrows():
                            st.write(f"• **{row['CATEGORIA'].title()}** consome **{row['PCT_RENDA_FMT']}** da sua renda.")
                        st.markdown("**Leitura de bolso:**")
                        st.write("• Moradia costuma ser o rei do tabuleiro.")
                        st.write("• Se a sobra estiver baixa, cortar miudeza ajuda menos do que parece.")
                        st.write("• Subcategoria que passa de 10% da renda já merece vigilância.")

                    st.markdown("---")
                    st.markdown("#### 🗂️ Resumo por categoria")
                    tabela_cat = df_cat[df_cat["CATEGORIA"] != "RENDA"].copy()
                    st.dataframe(
                        tabela_cat[["CATEGORIA", "VALOR_FMT", "PCT_RENDA_FMT", "FAIXA"]].rename(
                            columns={
                                "CATEGORIA": "Categoria",
                                "VALOR_FMT": "Total",
                                "PCT_RENDA_FMT": "% da renda",
                                "FAIXA": "Peso",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.markdown("---")
                    st.markdown("#### 🔎 Subcategorias com análise")
                    df_sub = df_itens[df_itens["CATEGORIA"] != "RENDA"].copy()
                    ordem_sub = {"MORADIA": 1, "ALIMENTAÇÃO": 2, "TRANSPORTE": 3, "OUTROS": 4}
                    df_sub["ORDEM"] = df_sub["CATEGORIA"].map(ordem_sub).fillna(99)
                    df_sub = df_sub.sort_values(["ORDEM", "PCT_RENDA"], ascending=[True, False])

                    st.dataframe(
                        df_sub[[
                            "CATEGORIA", "SUBCATEGORIA", "VALOR_FMT", "PCT_RENDA_FMT",
                            "PCT_CATEGORIA_FMT", "FAIXA", "ANALISE"
                        ]].rename(
                            columns={
                                "CATEGORIA": "Categoria",
                                "SUBCATEGORIA": "Subcategoria",
                                "VALOR_FMT": "Valor",
                                "PCT_RENDA_FMT": "% da renda",
                                "PCT_CATEGORIA_FMT": "% da categoria",
                                "FAIXA": "Peso",
                                "ANALISE": "Análise",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.markdown("---")
                    top_sub = df_sub.sort_values("PCT_RENDA", ascending=False).head(8)
                    st.markdown("#### 🎯 Itens que mais pesam na renda")
                    mapa_cores_sub = {
                        "MORADIA": "#72E0B5",
                        "ALIMENTAÇÃO": "#FFD36A",
                        "ALIMENTACAO": "#FFD36A",
                        "TRANSPORTE": "#6EA8FF",
                        "OUTROS": "#B497FF",
                    }
                    cores_sub = [mapa_cores_sub.get(cat, "#6EA8FF") for cat in top_sub["CATEGORIA"]]

                    fig_sub = go.Figure(go.Bar(
                        x=top_sub["SUBCATEGORIA"],
                        y=top_sub["VALOR"],
                        text=top_sub["VALOR_FMT"],
                        textposition="inside",
                        insidetextanchor="middle",
                        textfont=dict(size=12, color="#081018"),
                        marker=dict(color=cores_sub, line=dict(width=0)),
                        hovertemplate="<b>%{x}</b><br>%{text}<extra></extra>",
                    ))
                    fig_sub.update_layout(
                        template=tema,
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=420,
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis_title="",
                        yaxis_title="Valor (R$)",
                        uniformtext_minsize=9,
                        uniformtext_mode="hide",
                        font=dict(color="#e5edf7", size=12),
                        showlegend=False,
                    )
                    fig_sub.update_xaxes(showgrid=False)
                    fig_sub.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
                    st.plotly_chart(fig_sub, use_container_width=True)

                    st.markdown("#### 🛠️ Simulação rápida")
                    ajuste = st.slider(
                        "Se você reduzisse seus custos mensais, quanto conseguiria cortar?",
                        min_value=0,
                        max_value=1000,
                        value=200,
                        step=10,
                    )
                    nova_sobra = sobra_mes + ajuste
                    novo_pct_sobra = (nova_sobra / renda_total * 100) if renda_total > 0 else 0

                    s1, s2 = st.columns(2)
                    s1.metric("Nova sobra estimada", formato_real(nova_sobra))
                    s2.metric("Nova sobra em % da renda", format_pct(novo_pct_sobra))

                    st.markdown(
                        f'<div class="soft-note">Com um ajuste de <b>{formato_real(ajuste)}</b> por mês, sua sobra iria para <b>{formato_real(nova_sobra)}</b>, o que representa <b>{format_pct(novo_pct_sobra)}</b> da renda.</div>',
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                st.error(f"Erro ao montar o Projeto Morar Sozinho: {e}")
