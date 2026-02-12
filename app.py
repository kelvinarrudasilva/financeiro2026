import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

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
# FRASE
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Consistência vence motivação.",
    "Pequenos passos geram grandes resultados.",
    "Você está construindo algo grande."
]

st.title("🔑 Virada Financeira")
st.markdown(f'<div class="quote-card">{random.choice(FRASES)}</div>', unsafe_allow_html=True)

# =========================
# PLANILHA
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
# LEITURA
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

ano_atual = datetime.now().year

# =========================
# VISÃO GERAL DO ANO ATUAL
# =========================
st.subheader(f"📅 Visão Geral do Ano {ano_atual}")

rec_ano = receitas[receitas["ANO"] == ano_atual]["VALOR"].sum()
des_ano = despesas[despesas["ANO"] == ano_atual]["VALOR"].sum()
saldo_ano = rec_ano - des_ano

c1, c2, c3 = st.columns(3)
c1.metric("Receita no Ano", formato_real(rec_ano))
c2.metric("Despesa no Ano", formato_real(des_ano))
c3.metric("Saldo no Ano", formato_real(saldo_ano))

resumo_ano = (
    receitas[receitas["ANO"] == ano_atual]
    .groupby("MES_NUM", as_index=False)["VALOR"]
    .sum()
    .rename(columns={"VALOR":"RECEITA"})
)

des_ano_m = (
    despesas[despesas["ANO"] == ano_atual]
    .groupby("MES_NUM", as_index=False)["VALOR"]
    .sum()
    .rename(columns={"VALOR":"DESPESA"})
)

resumo_ano = pd.merge(resumo_ano, des_ano_m, on="MES_NUM", how="outer").fillna(0)
resumo_ano["SALDO"] = resumo_ano["RECEITA"] - resumo_ano["DESPESA"]
resumo_ano = resumo_ano.sort_values("MES_NUM")

fig_ano = go.Figure()

fig_ano.add_trace(go.Bar(
    x=resumo_ano["MES_NUM"],
    y=resumo_ano["RECEITA"],
    name="Receita"
))

fig_ano.add_trace(go.Bar(
    x=resumo_ano["MES_NUM"],
    y=resumo_ano["DESPESA"],
    name="Despesa"
))

fig_ano.add_trace(go.Scatter(
    x=resumo_ano["MES_NUM"],
    y=resumo_ano["SALDO"],
    mode="lines+markers",
    name="Saldo"
))

fig_ano.update_layout(barmode="group", height=400)
st.plotly_chart(fig_ano, use_container_width=True)

st.divider()

# =========================
# RESTANTE DO APP CONTINUA IGUAL
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")
resumo["MES_ANO"] = resumo["DATA_CHAVE"].dt.strftime("%b/%Y").str.upper()

# SELECTBOX DINÂMICO
hoje = datetime.now()
if hoje.month == 12:
    prox_mes = 1
    prox_ano = hoje.year + 1
else:
    prox_mes = hoje.month + 1
    prox_ano = hoje.year

mes_ref = datetime(prox_ano, prox_mes, 1).strftime("%b/%Y").upper()
lista_meses = resumo["MES_ANO"].tolist()
idx_default = lista_meses.index(mes_ref) if mes_ref in lista_meses else len(lista_meses)-1

mes_sel = st.selectbox("📅 Escolha o mês", lista_meses, index=idx_default)

mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

rec_mes = receitas[(receitas["ANO"]==ano_sel) & (receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel) & (despesas["MES"]==mes_txt)]

st.subheader(f"📆 Resumo — {mes_sel}")

d1, d2, d3 = st.columns(3)
d1.metric("Receitas", formato_real(rec_mes["VALOR"].sum()))
d2.metric("Despesas", formato_real(des_mes["VALOR"].sum()))
d3.metric("Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

st.divider()

st.subheader(f"💸 Despesas — {mes_sel}")

if not des_mes.empty:
    despesas_mes = des_mes.groupby("DESCRICAO", as_index=False)["VALOR"].sum().sort_values("VALOR", ascending=False)

    fig2 = px.bar(
        despesas_mes,
        x="VALOR",
        y="DESCRICAO",
        orientation="h",
        text=despesas_mes["VALOR"].apply(formato_real)
    )

    fig2.update_traces(textposition="inside")
    fig2.update_layout(height=500, yaxis=dict(autorange="reversed"))

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Nenhuma despesa registrada nesse mês.")
