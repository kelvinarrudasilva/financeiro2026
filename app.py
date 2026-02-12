import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="💰 Virada Financeira",
    page_icon="💸",
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
st.caption(random.choice(FRASES))

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
# LEITURA PRINCIPAL
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
# RESUMO
# =========================
rec_m = receitas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"RECEITA"})
des_m = despesas.groupby(["ANO","MES_NUM","MES"], as_index=False)["VALOR"].sum().rename(columns={"VALOR":"DESPESA"})

resumo = pd.merge(rec_m, des_m, on=["ANO","MES_NUM","MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO","MES_NUM"])
resumo["DATA_CHAVE"] = pd.to_datetime(resumo["ANO"].astype(str) + "-" + resumo["MES_NUM"].astype(str) + "-01")
resumo["MES_ANO"] = resumo["DATA_CHAVE"].dt.strftime("%b/%Y").str.upper()

# =========================
# VISÃO GERAL DO ANO
# =========================
st.subheader("📊 Visão Geral do Ano")

ano_atual = datetime.now().year
resumo_ano = resumo[resumo["ANO"] == ano_atual]

total_receita_ano = resumo_ano["RECEITA"].sum()
total_despesa_ano = resumo_ano["DESPESA"].sum()
saldo_ano = resumo_ano["SALDO"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Receita no Ano", formato_real(total_receita_ano))
c2.metric("Despesa no Ano", formato_real(total_despesa_ano))
c3.metric("Saldo no Ano", formato_real(saldo_ano))

# =========================
# SALDO RESTANTE
# =========================
mes_atual = datetime.now().month

saldo_restante = resumo_ano[
    resumo_ano["MES_NUM"] >= mes_atual
]["SALDO"].sum()

mes_inicio_txt = datetime(ano_atual, mes_atual, 1).strftime("%b").capitalize()

st.markdown(f"### 💰 Saldo Restante ({mes_inicio_txt}. a Dez.)")
st.markdown(f"## {formato_real(saldo_restante)}")

# =========================
# INVESTIDO (ABA INVESTIMENTO - LINHA 14)
# =========================
try:
    investimento_df = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO")
    linha_14 = investimento_df.iloc[13]  # índice 13 = linha 14

    valor_investido = 0.0
    for valor in linha_14:
        valor_convertido = limpar_valor(valor)
        if valor_convertido > 0:
            valor_investido = valor_convertido
            break

except:
    valor_investido = 0.0

st.markdown("### 📈 Investido")
st.markdown(f"## {formato_real(valor_investido)}")

# =========================
# GRÁFICO GERAL
# =========================
st.subheader("📈 Balanço Financeiro Geral")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["RECEITA"],
    name="Receita",
    text=resumo["RECEITA"].apply(formato_real),
    textposition="inside"
))

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["DESPESA"],
    name="Despesa",
    text=resumo["DESPESA"].apply(formato_real),
    textposition="inside"
))

fig.add_trace(go.Bar(
    x=resumo["MES_ANO"],
    y=resumo["SALDO"],
    name="Saldo",
    text=resumo["SALDO"].apply(formato_real),
    textposition="inside"
))

fig.update_layout(barmode="group", height=500)
st.plotly_chart(fig, use_container_width=True)

# =========================
# SELECTBOX DINÂMICO
# =========================
if datetime.now().month == 12:
    prox_mes = 1
    prox_ano = datetime.now().year + 1
else:
    prox_mes = datetime.now().month + 1
    prox_ano = datetime.now().year

mes_ref = datetime(prox_ano, prox_mes, 1).strftime("%b/%Y").upper()

lista_meses = resumo["MES_ANO"].tolist()
idx_default = lista_meses.index(mes_ref) if mes_ref in lista_meses else len(lista_meses)-1

mes_sel = st.selectbox("📅 Escolha o mês", lista_meses, index=idx_default)

mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

rec_mes = receitas[(receitas["ANO"]==ano_sel) & (receitas["MES"]==mes_txt)]
des_mes = despesas[(despesas["ANO"]==ano_sel) & (despesas["MES"]==mes_txt)]

st.subheader(f"📆 Resumo — {mes_sel}")

c1, c2, c3 = st.columns(3)
c1.metric("Receitas", formato_real(rec_mes["VALOR"].sum()))
c2.metric("Despesas", formato_real(des_mes["VALOR"].sum()))
c3.metric("Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

# =========================
# GRÁFICO DESPESAS DO MÊS
# =========================
st.subheader("💸 Despesas do Mês Selecionado")

if not des_mes.empty:
    despesas_total = (
        des_mes.groupby("DESCRICAO", as_index=False)["VALOR"]
        .sum()
        .sort_values("VALOR", ascending=False)
    )

    fig2 = go.Figure(go.Bar(
        x=despesas_total["DESCRICAO"],
        y=despesas_total["VALOR"],
        text=despesas_total["VALOR"].apply(formato_real),
        textposition="inside"
    ))

    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Sem despesas neste mês.")
