import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="💰 Virada Financeira PRO",
    page_icon="💎",
    layout="wide"
)

# =========================
# FRASE
# =========================
FRASES = [
    "Disciplina constrói liberdade.",
    "Consistência vence motivação.",
    "Pequenos passos geram grandes resultados.",
    "Você está construindo algo grande."
]

st.title("💎 Virada Financeira PRO")
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
# ANO ATUAL
# =========================
ano_atual = datetime.now().year
mes_atual = datetime.now().month

resumo_ano = resumo[resumo["ANO"] == ano_atual]

total_receita_ano = resumo_ano["RECEITA"].sum()
total_despesa_ano = resumo_ano["DESPESA"].sum()
saldo_ano = resumo_ano["SALDO"].sum()

saldo_restante = resumo_ano[
    resumo_ano["MES_NUM"] > mes_atual
]["SALDO"].sum()

# =========================
# INVESTIMENTO
# =========================
try:
    investimento_df = pd.read_excel(PLANILHA_URL, sheet_name="INVESTIMENTO", header=None)
    valor_investido = limpar_valor(investimento_df.iloc[13, 1])
except:
    valor_investido = 0.0

# =========================
# PROJEÇÃO BASEADA EM MÉDIA REAL
# =========================
meses_passados = resumo_ano[resumo_ano["MES_NUM"] <= mes_atual]

if len(meses_passados) > 0:
    media_saldo = meses_passados["SALDO"].mean()
else:
    media_saldo = 0

meses_restantes = 12 - mes_atual
projecao_final_ano = saldo_ano + (media_saldo * meses_restantes)

patrimonio_projetado = valor_investido + projecao_final_ano

# =========================
# MÉTRICAS
# =========================
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("💵 Receita Ano", formato_real(total_receita_ano))
c2.metric("💸 Despesa Ano", formato_real(total_despesa_ano))
c3.metric("🏦 Saldo Ano", formato_real(saldo_ano))
c4.metric("🧭 Saldo Restante", formato_real(saldo_restante))
c5.metric("📈 Investido", formato_real(valor_investido))
c6.metric("🔮 Projeção Final Ano", formato_real(projecao_final_ano))

st.markdown("---")

# =========================
# EXPLICAÇÃO DA PROJEÇÃO
# =========================
st.info(
"""
🔎 **Base da Projeção**

A projeção é calculada utilizando a **média real do saldo mensal já realizado no ano atual**.

Fórmula aplicada:

Projeção = Saldo acumulado atual  
+ (Média dos saldos já realizados × Meses restantes do ano)

Não é chute.  
É estatística simples baseada no seu próprio comportamento financeiro.
"""
)

# =========================
# GRÁFICO PROJEÇÃO
# =========================
st.subheader("📊 Evolução e Projeção do Patrimônio")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=resumo_ano["MES_ANO"],
    y=resumo_ano["SALDO"],
    name="Saldo Real"
))

fig.add_trace(go.Scatter(
    x=["Projeção Dez"],
    y=[projecao_final_ano],
    mode="markers+text",
    name="Projeção",
    text=[formato_real(projecao_final_ano)],
    textposition="top center"
))

fig.update_layout(
    template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.success(f"💎 Patrimônio Projetado (Saldo + Investido): {formato_real(patrimonio_projetado)}")
