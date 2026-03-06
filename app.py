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

st.title("💎 Virada Financeira")
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
        except Exception:
            return 0.0
    try:
        return float(v)
    except Exception:
        return 0.0


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
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce", dayfirst=True)
    base = base.dropna(subset=["DATA"])

    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.upper()

    return base


def preparar_gastos_variaveis(df_gastos):
    df_gastos = normalizar_colunas(df_gastos.copy())

    mapa = {}
    for col in df_gastos.columns:
        if "DATA" in col and "DATA" not in mapa:
            mapa[col] = "DATA"
        elif "MES" in col and "MES" not in mapa:
            mapa[col] = "MES"
        elif ("NOME" in col or "DESCR" in col) and "NOME" not in mapa:
            mapa[col] = "NOME"
        elif ("FORMA" in col and "PAG" in col) and "FORMA PAGAMENTO" not in mapa:
            mapa[col] = "FORMA PAGAMENTO"
        elif "CLASSIFIC" in col and "CLASSIFICACAO" not in mapa:
            mapa[col] = "CLASSIFICACAO"
        elif "VALOR" in col and "VALOR" not in mapa:
            mapa[col] = "VALOR"

    df_gastos = df_gastos.rename(columns=mapa)

    for col in ["DATA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"]:
        if col not in df_gastos.columns:
            df_gastos[col] = None

    df_gastos = df_gastos[["DATA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"]].copy()
    df_gastos["DATA"] = pd.to_datetime(df_gastos["DATA"], errors="coerce", dayfirst=True)
    df_gastos["VALOR"] = df_gastos["VALOR"].apply(limpar_valor)
    df_gastos = df_gastos.dropna(subset=["DATA"])
    df_gastos = df_gastos[df_gastos["NOME"].notna()].copy()

    df_gastos["ANO"] = df_gastos["DATA"].dt.year
    df_gastos["MES_NUM"] = df_gastos["DATA"].dt.month
    df_gastos["MES_ANO"] = df_gastos["DATA"].dt.strftime("%b/%Y").str.upper()
    df_gastos["QUINZENA"] = df_gastos["DATA"].dt.day.apply(lambda x: "1ª quinzena" if x <= 15 else "2ª quinzena")
    df_gastos["DATA_FMT"] = df_gastos["DATA"].dt.strftime("%d/%m/%Y")
    df_gastos["CLASSIFICACAO"] = df_gastos["CLASSIFICACAO"].fillna("SEM CLASSIFICAÇÃO").astype(str).str.upper()
    df_gastos["FORMA PAGAMENTO"] = df_gastos["FORMA PAGAMENTO"].fillna("NÃO INFORMADO").astype(str).str.upper()
    df_gastos["NOME"] = df_gastos["NOME"].astype(str).str.strip()
    return df_gastos.sort_values("DATA", ascending=False)


@st.cache_data(show_spinner=False)
def carregar_planilha_excel(url):
    return pd.ExcelFile(url)


@st.cache_data(show_spinner=False)
def ler_planilha(url):
    return pd.read_excel(url)

# =========================
# LEITURA
# =========================
try:
    xls = carregar_planilha_excel(PLANILHA_URL)
    df = pd.read_excel(xls, sheet_name=0)
except Exception as e:
    st.error(f"Erro ao carregar planilha: {e}")
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
    investimento_df = pd.read_excel(xls, sheet_name="INVESTIMENTO", header=None)
    valor_investido = limpar_valor(investimento_df.iloc[13, 1])
except Exception:
    valor_investido = 0.0

patrimonio_em_construcao = saldo_restante + valor_investido

# =========================
# MÉTRICAS
# =========================
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("💵 Receita no Ano", formato_real(total_receita_ano))
c2.metric("💸 Despesa no Ano", formato_real(total_despesa_ano))
c3.metric("🏦 Saldo no Ano", formato_real(saldo_ano))
c4.metric("🧭 Saldo Restante", formato_real(saldo_restante))
c5.metric("📈 Investido", formato_real(valor_investido))
c6.metric("💎 Total em Construção", formato_real(patrimonio_em_construcao))

st.markdown("---")

# =========================
# GRÁFICO GERAL
# =========================
st.subheader("📊 Balanço Financeiro Geral")

tema = "plotly_dark" if st.get_option("theme.base") == "dark" else "plotly"

fig = go.Figure()

fig.add_bar(
    x=resumo["MES_ANO"],
    y=resumo["RECEITA"],
    name="Receita",
    text=resumo["RECEITA"].apply(formato_real),
    textposition="inside"
)

fig.add_bar(
    x=resumo["MES_ANO"],
    y=resumo["DESPESA"],
    name="Despesa",
    text=resumo["DESPESA"].apply(formato_real),
    textposition="inside"
)

fig.add_bar(
    x=resumo["MES_ANO"],
    y=resumo["SALDO"],
    name="Saldo",
    text=resumo["SALDO"].apply(formato_real),
    textposition="inside"
)

fig.update_layout(
    template=tema,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    barmode="group",
    uniformtext_minsize=8,
    uniformtext_mode="hide",
    height=500
)

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

mes_ref = datetime(prox_ano, prox_mes, 1).strftime("%b/%Y").upper()

lista_meses = resumo["MES_ANO"].tolist()

if mes_ref in lista_meses:
    idx_default = lista_meses.index(mes_ref)
else:
    idx_default = len(lista_meses) - 1 if lista_meses else 0

mes_sel = st.selectbox("📅 Escolha o mês", lista_meses, index=idx_default)

mes_txt, ano_sel = mes_sel.split("/")
ano_sel = int(ano_sel)

rec_mes = receitas[(receitas["ANO"] == ano_sel) & (receitas["MES"] == mes_txt)]
des_mes = despesas[(despesas["ANO"] == ano_sel) & (despesas["MES"] == mes_txt)]

st.subheader(f"📆 Resumo — {mes_sel}")

c1, c2, c3 = st.columns(3)
c1.metric("💵 Receitas", formato_real(rec_mes["VALOR"].sum()))
c2.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
c3.metric("🏦 Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

# =========================
# GRÁFICO DESPESAS
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

    fig2.update_layout(
        template=tema,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=500
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Sem despesas neste mês.")

# =========================
# GASTOS VARIÁVEIS — SÓ UMA TABELINHA + UM GRÁFICO
# =========================
st.markdown("---")
st.subheader("🧾 Gastos variáveis")
st.caption("Controle simples do que saiu fora dos gastos fixos, por mês e por quinzena.")

nomes_abas_gastos = [
    "GASTOS", "GASTOS_VARIAVEIS", "GASTOS VARIAVEIS", "GASTOS EXTRAS", "VARIAVEIS"
]

aba_gastos_encontrada = next((nome for nome in nomes_abas_gastos if nome in xls.sheet_names), None)

if aba_gastos_encontrada is None:
    st.info(
        "Não encontrei uma aba de gastos variáveis na planilha. "
        "Crie uma aba como no print com colunas: DATA, MÊS, NOME, FORMA PAGAMENTO, CLASSIFICAÇÃO e VALOR."
    )
else:
    try:
        gastos_raw = pd.read_excel(xls, sheet_name=aba_gastos_encontrada)
        gastos = preparar_gastos_variaveis(gastos_raw)
    except Exception:
        gastos = pd.DataFrame()

    if gastos.empty:
        st.info("A aba de gastos foi encontrada, mas ainda está vazia ou com colunas fora do padrão.")
    else:
        meses_gastos = sorted(gastos["MES_ANO"].dropna().unique().tolist(), reverse=True)
        idx_gasto = meses_gastos.index(mes_sel) if mes_sel in meses_gastos else 0

        c_f1, c_f2 = st.columns([2, 1])
        with c_f1:
            mes_gasto_sel = st.selectbox("📅 Mês dos gastos", meses_gastos, index=idx_gasto)
        with c_f2:
            quinzena_sel = st.selectbox("🌓 Quinzena", ["Todas", "1ª quinzena", "2ª quinzena"], index=0)

        gastos_filt = gastos[gastos["MES_ANO"] == mes_gasto_sel].copy()
        if quinzena_sel != "Todas":
            gastos_filt = gastos_filt[gastos_filt["QUINZENA"] == quinzena_sel].copy()

        g1, g2, g3 = st.columns(3)
        g1.metric("💸 Total gasto", formato_real(gastos_filt["VALOR"].sum()))
        g2.metric("🧾 Lançamentos", int(len(gastos_filt)))
        g3.metric("📉 Ticket médio", formato_real(gastos_filt["VALOR"].mean() if not gastos_filt.empty else 0.0))

        col_graf, col_tab = st.columns([1.1, 1.4])

        with col_graf:
            st.markdown("#### 📊 Gastos por classificação")
            if gastos_filt.empty:
                st.info("Sem gastos no filtro escolhido.")
            else:
                graf_gastos = (
                    gastos_filt.groupby("CLASSIFICACAO", as_index=False)["VALOR"]
                    .sum()
                    .sort_values("VALOR", ascending=False)
                )

                fig3 = go.Figure(go.Bar(
                    x=graf_gastos["CLASSIFICACAO"],
                    y=graf_gastos["VALOR"],
                    text=graf_gastos["VALOR"].apply(formato_real),
                    textposition="inside"
                ))
                fig3.update_layout(
                    template=tema,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=420,
                    margin=dict(l=10, r=10, t=20, b=10)
                )
                st.plotly_chart(fig3, use_container_width=True)

        with col_tab:
            st.markdown("#### 📋 Tabela de gastos")
            if gastos_filt.empty:
                st.info("Sem lançamentos nesse período.")
            else:
                tabela_gastos = gastos_filt[[
                    "DATA_FMT", "QUINZENA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"
                ]].copy()
                tabela_gastos["VALOR"] = tabela_gastos["VALOR"].map(formato_real)
                tabela_gastos = tabela_gastos.rename(columns={
                    "DATA_FMT": "Data",
                    "QUINZENA": "Quinzena",
                    "NOME": "Nome",
                    "FORMA PAGAMENTO": "Forma pagamento",
                    "CLASSIFICACAO": "Classificação",
                    "VALOR": "Valor"
                })
                st.dataframe(tabela_gastos, use_container_width=True, hide_index=True, height=420)
