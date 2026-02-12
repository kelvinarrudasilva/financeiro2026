import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

st.set_page_config(page_title="💰 Virada Financeira PRO", page_icon="🚀", layout="wide")

# =========================
# FRASE
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Você não está organizando dinheiro. Está construindo patrimônio.",
    "Consistência cria patrimônio invisível.",
    "O futuro recompensa quem calcula."
]

st.title("🚀 Virada Financeira")
st.caption(random.choice(FRASES))

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
    return float(v)

def formato_real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def normalizar(df):
    df.columns = df.columns.str.upper().str.strip()
    return df

def preparar(base):
    base = normalizar(base)
    base.columns = ["DATA","DESC","VALOR"]
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base["ANO"] = base["DATA"].dt.year
    base["MES"] = base["DATA"].dt.month
    return base

# =========================
# LEITURA
# =========================
df = pd.read_excel(PLANILHA_URL)
df = normalizar(df)

meio = len(df.columns)//2
receitas = preparar(df.iloc[:,:meio].copy())
despesas = preparar(df.iloc[:,meio:].copy())

rec = receitas.groupby(["ANO","MES"], as_index=False)["VALOR"].sum()
des = despesas.groupby(["ANO","MES"], as_index=False)["VALOR"].sum()

resumo = pd.merge(rec, des, on=["ANO","MES"], how="outer", suffixes=("_REC","_DES")).fillna(0)
resumo["SALDO"] = resumo["VALOR_REC"] - resumo["VALOR_DES"]

ano_atual = datetime.now().year
mes_atual = datetime.now().month

res_ano = resumo[resumo["ANO"]==ano_atual]

receita_ano = res_ano["VALOR_REC"].sum()
despesa_ano = res_ano["VALOR_DES"].sum()
saldo_ano = res_ano["SALDO"].sum()

saldo_restante = res_ano[res_ano["MES"] > mes_atual]["SALDO"].sum()

# INVESTIDO
try:
    inv_df = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO", header=None)
    investido = limpar_valor(inv_df.iloc[13,1])
except:
    investido = 0

# =========================
# MÉTRICAS PRINCIPAIS
# =========================
col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("💵 Receita no Ano", formato_real(receita_ano))
col2.metric("💸 Despesa no Ano", formato_real(despesa_ano))
col3.metric("🏦 Saldo no Ano", formato_real(saldo_ano))
col4.metric("🧭 Saldo Restante", formato_real(saldo_restante))
col5.metric("📈 Investido", formato_real(investido))

# =========================
# NOVAS MÉTRICAS AVANÇADAS
# =========================
st.divider()
st.subheader("📊 Inteligência Financeira")

taxa_economia = (saldo_ano/receita_ano*100) if receita_ano>0 else 0
patrimonio_projetado = investido + saldo_restante

media_saldo = res_ano["SALDO"].mean()
meses_restantes = 12 - mes_atual
projecao_conservadora = investido + (media_saldo * meses_restantes)

colA,colB,colC = st.columns(3)

colA.metric("📌 Taxa de Economia", f"{taxa_economia:.1f}%")
colB.metric("💎 Patrimônio Projetado", formato_real(patrimonio_projetado))
colC.metric("🔮 Projeção Conservadora", formato_real(projecao_conservadora))

# =========================
# RISCO FINANCEIRO
# =========================
st.subheader("⚠️ Indicador de Risco")

if receita_ano > 0:
    consumo = despesa_ano/receita_ano*100
else:
    consumo = 0

if consumo > 85:
    st.error(f"🔴 Alto risco — {consumo:.1f}% da receita está sendo consumida.")
elif consumo > 70:
    st.warning(f"🟡 Atenção — {consumo:.1f}% da receita comprometida.")
else:
    st.success(f"🟢 Saudável — {consumo:.1f}% da receita comprometida.")

# =========================
# PROGRESSO VISUAL DO ANO
# =========================
st.subheader("📈 Progresso Financeiro do Ano")

fig = go.Figure()

fig.add_bar(name="Receita", x=["Ano"], y=[receita_ano])
fig.add_bar(name="Despesa", x=["Ano"], y=[despesa_ano])
fig.add_bar(name="Saldo", x=["Ano"], y=[saldo_ano])

fig.update_layout(
    template="plotly",
    barmode="group",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig, use_container_width=True)
