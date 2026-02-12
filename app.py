import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import requests
import random
import os

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="💰 Virada Financeira",
    page_icon="🗝️",
    layout="wide"
)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #0e0e11;
}
.block-container {
    padding-top: 2rem;
    max-width: 1300px;
}
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #16161d, #1b1b24);
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #1f1f2b;
}
.quote-card {
    background: linear-gradient(145deg, #1b1b24, #16161d);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #1f1f2b;
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
    color: #9ca3af;
    font-style: italic;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FRASE DIÁRIA
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Pequenos passos geram grandes resultados.",
    "Consistência vence motivação.",
    "Você está construindo algo grande."
]

st.title("🔑 Virada Financeira")
st.markdown(f'<div class="quote-card">{random.choice(FRASES)}</div>', unsafe_allow_html=True)

# =========================
# PLANILHA GOOGLE
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

def normalizar_colunas(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    return df

def preparar_base(base):
    base = normalizar_colunas(base)

    col_data = [c for c in base.columns if "DATA" in c][0]
    col_valor = [c for c in base.columns if "VALOR" in c][0]
    col_desc = [c for c in base.columns if "NOME" in c or "DESCR" in c][0]

    base = base[[col_data, col_desc, col_valor]].copy()
    base.columns = ["DATA", "DESCRICAO", "VALOR"]

    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base = base.dropna(subset=["DATA"])

    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.upper()

    return base

# =========================
# LEITURA DA PLANILHA
# =========================
try:
    df = pd.read_excel(PLANILHA_URL)
except:
    st.error("Erro ao carregar planilha.")
    st.stop()

df = normalizar_colunas(df)

meio = len(df.columns) // 2
receitas = preparar_base(df.iloc[:, :meio].copy())
despesas = preparar_base(df.iloc[:, meio:].copy())

# =========================
# MÉTRICAS GERAIS
# =========================
st.subheader("📌 Visão Geral")
c1, c2, c3 = st.columns(3)
c1.metric("Receita Total", formato_real(receitas["VALOR"].sum()))
c2.metric("Despesa Total", formato_real(despesas["VALOR"].sum()))
c3.metric("Saldo Geral", formato_real(receitas["VALOR"].sum() - despesas["VALOR"].sum()))

st.divider()

# =========================
# RESUMO MENSAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")
resumo["MES_ANO"] = resumo["DATA_CHAVE"].dt.strftime("%b/%Y").str.upper()

# =========================
# SELECTBOX DINÂMICO (PRÓXIMO MÊS)
# =========================
hoje = datetime.now()
if hoje.month == 12:
    prox_mes = 1
    prox_ano = hoje.year + 1
else:
    prox_mes = hoje.month + 1
    prox_ano = hoje.year

mes_ref = datetime(prox_ano, prox_mes, 1).strftime("%b/%Y").upper()
lista_meses = resumo["MES_ANO"].tolist()

if mes_ref in lista_meses:
    idx_default = lista_meses.index(mes_ref)
else:
    idx_default = len(lista_meses)-1 if lista_meses else 0

mes_sel = st.selectbox("📅 Escolha o mês", lista_meses, index=idx_default)

# =========================
# DETALHAMENTO
# =========================
mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

rec_mes = receitas[(receitas["ANO"]==ano_sel) & (receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel) & (despesas["MES"]==mes_txt)]

st.subheader(f"📆 Detalhamento — {mes_sel}")

d1, d2, d3 = st.columns(3)
d1.metric("Receitas", formato_real(rec_mes["VALOR"].sum()))
d2.metric("Despesas", formato_real(des_mes["VALOR"].sum()))
d3.metric("Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

# =========================
# GRÁFICO GERAL DE DESPESAS
# =========================
st.divider()
st.subheader("💸 Todas as Despesas (visão geral)")

if not despesas.empty:

    despesas_total = (
        despesas
        .groupby("DESCRICAO", as_index=False)["VALOR"]
        .sum()
        .sort_values("VALOR", ascending=False)
    )

    fig_despesas = px.bar(
        despesas_total,
        x="VALOR",
        y="DESCRICAO",
        orientation="h",
        text=despesas_total["VALOR"].apply(formato_real),
        title="Total gasto por categoria"
    )

    fig_despesas.update_traces(textposition="inside")
    fig_despesas.update_layout(
        height=500,
        yaxis=dict(autorange="reversed")
    )

    st.plotly_chart(fig_despesas, use_container_width=True)

else:
    st.info("Nenhuma despesa encontrada.")
