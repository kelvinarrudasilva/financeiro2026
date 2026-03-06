import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random
import unicodedata

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
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base = base.dropna(subset=["DATA"])

    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.upper()

    return base


@st.cache_data(show_spinner=False)
def carregar_aba_principal(url):
    return pd.read_excel(url)


@st.cache_data(show_spinner=False)
def listar_abas(url):
    xls = pd.ExcelFile(url)
    return xls.sheet_names


@st.cache_data(show_spinner=False)
def carregar_aba(url, sheet_name, header=0):
    return pd.read_excel(url, sheet_name=sheet_name, header=header)


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
            "DATA", "MES", "QUINZENA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR", "ANO", "MES_NUM", "MES_ANO"
        ])

    df = normalizar_colunas(df)

    mapa = {}
    for c in df.columns:
        if "DATA" in c and "DATA" not in mapa.values():
            mapa[c] = "DATA"
        elif (c == "MES" or "MES" in c) and "MES" not in mapa.values():
            mapa[c] = "MES"
        elif ("NOME" in c or "DESCR" in c) and "NOME" not in mapa.values():
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
            "DATA", "MES", "QUINZENA", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR", "ANO", "MES_NUM", "MES_ANO"
        ])

    for col in ["FORMA PAGAMENTO", "CLASSIFICACAO", "MES"]:
        if col not in df.columns:
            df[col] = ""

    df = df[["DATA", "MES", "NOME", "FORMA PAGAMENTO", "CLASSIFICACAO", "VALOR"]].copy()
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce", dayfirst=True)
    df["VALOR"] = df["VALOR"].apply(limpar_valor)
    df = df.dropna(subset=["DATA"])
    df = df[df["NOME"].astype(str).str.strip() != ""]

    df["QUINZENA"] = df["DATA"].dt.day.apply(lambda x: "1ª quinzena" if x <= 15 else "2ª quinzena")
    df["ANO"] = df["DATA"].dt.year
    df["MES_NUM"] = df["DATA"].dt.month
    df["MES_ANO"] = df["DATA"].dt.strftime("%b/%Y").str.upper()

    mes_limpo = df["MES"].astype(str).str.strip()
    df["MES"] = mes_limpo.where(mes_limpo != "", df["DATA"].dt.strftime("%b").str.upper())

    return df.sort_values("DATA", ascending=False)


# =========================
# LEITURA
# =========================
try:
    df = carregar_aba_principal(PLANILHA_URL)
    nomes_abas = listar_abas(PLANILHA_URL)
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
    investimento_df = carregar_aba(PLANILHA_URL, "INVESTIMENTO", header=None)
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
fig.add_bar(x=resumo["MES_ANO"], y=resumo["RECEITA"], name="Receita", text=resumo["RECEITA"].apply(formato_real), textposition="inside")
fig.add_bar(x=resumo["MES_ANO"], y=resumo["DESPESA"], name="Despesa", text=resumo["DESPESA"].apply(formato_real), textposition="inside")
fig.add_bar(x=resumo["MES_ANO"], y=resumo["SALDO"], name="Saldo", text=resumo["SALDO"].apply(formato_real), textposition="inside")
fig.update_layout(
    template=tema,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    barmode="group",
    uniformtext_minsize=8,
    uniformtext_mode="hide",
    height=500,
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

if lista_meses:
    idx_default = lista_meses.index(mes_ref) if mes_ref in lista_meses else len(lista_meses) - 1
    mes_sel = st.selectbox("📅 Escolha o mês", lista_meses, index=idx_default)

    mes_txt, ano_sel = mes_sel.split("/")
    ano_sel = int(ano_sel)

    rec_mes = receitas[(receitas["ANO"] == ano_sel) & (receitas["MES"] == mes_txt)]
    des_mes = despesas[(despesas["ANO"] == ano_sel) & (despesas["MES"] == mes_txt)]

    st.subheader(f"📆 Resumo — {mes_sel}")
    r1, r2, r3 = st.columns(3)
    r1.metric("💵 Receitas", formato_real(rec_mes["VALOR"].sum()))
    r2.metric("💸 Despesas", formato_real(des_mes["VALOR"].sum()))
    r3.metric("🏦 Saldo", formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum()))

    st.subheader("💸 Despesas do Mês Selecionado")
    if not des_mes.empty:
        despesas_total = (
            des_mes.groupby("DESCRICAO", as_index=False)["VALOR"]
            .sum()
            .sort_values("VALOR", ascending=False)
        )
        despesas_total = despesas_total[despesas_total["DESCRICAO"].astype(str).str.strip() != ""]

        if despesas_total.empty:
            st.info("Sem despesas válidas neste mês.")
        else:
            fig2 = go.Figure(go.Bar(
                x=despesas_total["DESCRICAO"],
                y=despesas_total["VALOR"],
                text=despesas_total["VALOR"].apply(formato_real),
                textposition="outside"
            ))
            fig2.update_layout(
                template=tema,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=340,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="",
                yaxis_title="",
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Sem despesas neste mês.")
else:
    st.info("Não encontrei meses válidos na base principal.")

# =========================
# GASTOS VARIÁVEIS — SÓ TABELA + GRÁFICO
# =========================
st.markdown("---")
st.subheader("🧾 Gastos variáveis")
st.caption("Uma tabelinha e um gráfico para acompanhar o que saiu fora dos gastos fixos.")

aba_gastos = encontrar_aba_gastos(nomes_abas)

if not aba_gastos:
    st.info("Não encontrei uma aba de gastos variáveis. Use uma aba como GASTOS com colunas DATA, MÊS, NOME, FORMA PAGAMENTO, CLASSIFICAÇÃO e VALOR.")
else:
    try:
        gastos_raw = carregar_aba(PLANILHA_URL, aba_gastos)
    except Exception:
        gastos_raw = pd.DataFrame()

    gastos = preparar_gastos(gastos_raw)

    if gastos.empty:
        st.warning(f"Encontrei a aba '{aba_gastos}', mas não consegui montar a base de gastos.")
    else:
        meses_gastos = sorted(gastos["MES_ANO"].dropna().unique().tolist(), reverse=True)
        mes_padrao = datetime.now().strftime("%b/%Y").upper()
        idx_mes_gasto = meses_gastos.index(mes_padrao) if mes_padrao in meses_gastos else 0

        f1, f2 = st.columns([2, 1])
        with f1:
            mes_gasto_sel = st.selectbox("📅 Mês dos gastos", meses_gastos, index=idx_mes_gasto)
        with f2:
            quinzena_sel = st.selectbox("🗓️ Quinzena", ["Todas", "1ª quinzena", "2ª quinzena"], index=0)

        gastos_filt = gastos[gastos["MES_ANO"] == mes_gasto_sel].copy()
        if quinzena_sel != "Todas":
            gastos_filt = gastos_filt[gastos_filt["QUINZENA"] == quinzena_sel].copy()

        g1, g2 = st.columns([1.05, 1.35])
        with g1:
            total_gastos = gastos_filt["VALOR"].sum()
            qtd_lanc = len(gastos_filt)
            st.metric("💸 Total do período", formato_real(total_gastos))
            st.metric("🧾 Lançamentos", str(qtd_lanc))

            classif = gastos_filt.copy()
            if not classif.empty:
                classif["CLASSIFICACAO"] = classif["CLASSIFICACAO"].replace("", "SEM CLASSIFICAÇÃO")
                graf_class = classif.groupby("CLASSIFICACAO", as_index=False)["VALOR"].sum().sort_values("VALOR", ascending=False)

                fig3 = go.Figure(go.Bar(
                    x=graf_class["CLASSIFICACAO"],
                    y=graf_class["VALOR"],
                    text=graf_class["VALOR"].apply(formato_real),
                    textposition="outside"
                ))
                fig3.update_layout(
                    template=tema,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    height=320,
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis_title="",
                    yaxis_title="",
                    showlegend=False,
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Sem gastos nesse filtro.")

        with g2:
            tabela_gastos = gastos_filt.copy()
            tabela_gastos["DATA"] = tabela_gastos["DATA"].dt.strftime("%d/%m/%Y")
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
                tabela_gastos[["Data", "Mês", "Quinzena", "Nome", "Forma pagamento", "Classificação", "VALOR_FMT"]]
                .rename(columns={"VALOR_FMT": "Valor"}),
                use_container_width=True,
                hide_index=True,
                height=420,
            )
