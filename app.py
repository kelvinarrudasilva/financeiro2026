import random
import unicodedata
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="💰 Virada Financeira",
    page_icon="💎",
    layout="wide",
)

PLANILHA_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lI55tMA0GkpZ2D4EF8PPHQ4d5z3NNAKH"
    "/export?format=xlsx"
)

FRASES = [
    "Disciplina constrói liberdade.",
    "Consistência vence motivação.",
    "Pequenos passos geram grandes resultados.",
    "Você está construindo algo grande.",
]

MESES_PT = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}

# =========================
# CSS
# =========================
st.markdown(
    """
<style>
    .stApp {
        background: linear-gradient(180deg, #070b12 0%, #0d1117 100%);
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .hero {
        background: linear-gradient(135deg, rgba(16,185,129,.18), rgba(59,130,246,.16));
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 24px;
        padding: 20px 22px;
        margin-bottom: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,.18);
    }
    .hero h1 {
        margin: 0;
        font-size: 2rem;
    }
    .hero p {
        margin: .25rem 0 0 0;
        color: #b6c2cf;
    }
    .section-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 22px;
        padding: 16px 18px;
        margin-bottom: 14px;
        backdrop-filter: blur(6px);
    }
    .tiny-note {
        color: #93a3b8;
        font-size: 0.88rem;
    }
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,.06);
        border-radius: 18px;
        padding: 14px 12px;
    }
    div[data-testid="stDataFrame"] div[role="grid"] {
        border-radius: 16px;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] [role="row"]:hover {
        background: rgba(16,185,129,.10) !important;
    }
    .pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: .85rem;
        background: rgba(16,185,129,.12);
        border: 1px solid rgba(16,185,129,.28);
        color: #d8fff4;
        margin-right: 8px;
        margin-bottom: 8px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# HELPERS
# =========================
def strip_accents(text: str) -> str:
    text = str(text)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", text) if not unicodedata.combining(ch)
    )


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [strip_accents(c).strip().upper() for c in out.columns]
    return out


def limpar_valor(v) -> float:
    if pd.isna(v):
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
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


def formato_real(v) -> str:
    try:
        v = float(v)
    except Exception:
        v = 0.0
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mes_ano_pt(dt_series: pd.Series) -> pd.Series:
    return dt_series.dt.month.map(MESES_PT) + "/" + dt_series.dt.year.astype(str)


def preparar_base(base: pd.DataFrame) -> pd.DataFrame:
    base = normalizar_colunas(base)

    col_data = next((c for c in base.columns if "DATA" in c), None)
    col_valor = next((c for c in base.columns if "VALOR" in c), None)
    col_desc = next((c for c in base.columns if "NOME" in c or "DESCR" in c), None)

    if not all([col_data, col_valor, col_desc]):
        return pd.DataFrame(columns=["DATA", "DESCRICAO", "VALOR", "ANO", "MES_NUM", "MES"])

    out = base[[col_data, col_desc, col_valor]].copy()
    out.columns = ["DATA", "DESCRICAO", "VALOR"]
    out["VALOR"] = out["VALOR"].apply(limpar_valor)
    out["DATA"] = pd.to_datetime(out["DATA"], errors="coerce", dayfirst=True)
    out = out.dropna(subset=["DATA"])

    out["ANO"] = out["DATA"].dt.year
    out["MES_NUM"] = out["DATA"].dt.month
    out["MES"] = out["MES_NUM"].map(MESES_PT)
    return out


def identificar_quinzena(dia: int) -> str:
    return "1ª quinzena" if int(dia) <= 15 else "2ª quinzena"


@st.cache_data(show_spinner=False)
def carregar_planilha(url: str):
    xls = pd.ExcelFile(url)
    principal = pd.read_excel(url)
    nomes_abas = xls.sheet_names
    return principal, nomes_abas


@st.cache_data(show_spinner=False)
def ler_aba(url: str, nome_aba: str):
    return pd.read_excel(url, sheet_name=nome_aba)


def detectar_aba_gastos(nomes_abas: list[str]) -> str | None:
    prioridades = [
        "GASTOS",
        "GASTOS_VARIAVEIS",
        "GASTOS VARIAVEIS",
        "EXTRAS",
        "SAIDAS_EXTRAS",
        "SAIDAS EXTRAS",
    ]
    mapa = {strip_accents(a).upper(): a for a in nomes_abas}
    for p in prioridades:
        if p in mapa:
            return mapa[p]
    return None


def preparar_gastos(df_gastos: pd.DataFrame) -> pd.DataFrame:
    if df_gastos is None or df_gastos.empty:
        return pd.DataFrame(
            columns=[
                "DATA",
                "MES",
                "NOME",
                "FORMA PAGAMENTO",
                "CLASSIFICACAO",
                "VALOR",
                "ANO",
                "MES_NUM",
                "MES_ANO",
                "QUINZENA",
            ]
        )

    df = normalizar_colunas(df_gastos)

    col_data = next((c for c in df.columns if "DATA" in c), None)
    col_nome = next((c for c in df.columns if "NOME" in c or "DESCR" in c), None)
    col_forma = next((c for c in df.columns if "FORMA" in c or "PAGAMENTO" in c), None)
    col_class = next((c for c in df.columns if "CLASS" in c), None)
    col_valor = next((c for c in df.columns if "VALOR" in c), None)

    base = pd.DataFrame()
    base["DATA"] = pd.to_datetime(df[col_data], errors="coerce", dayfirst=True) if col_data else pd.NaT
    base["NOME"] = df[col_nome].astype(str).str.strip() if col_nome else ""
    base["FORMA PAGAMENTO"] = df[col_forma].astype(str).str.strip() if col_forma else "Não informado"
    base["CLASSIFICACAO"] = df[col_class].astype(str).str.strip() if col_class else "Sem classificação"
    base["VALOR"] = df[col_valor].apply(limpar_valor) if col_valor else 0.0

    base = base.dropna(subset=["DATA"])
    base = base[base["NOME"].astype(str).str.strip() != ""]

    if base.empty:
        return pd.DataFrame(
            columns=[
                "DATA",
                "MES",
                "NOME",
                "FORMA PAGAMENTO",
                "CLASSIFICACAO",
                "VALOR",
                "ANO",
                "MES_NUM",
                "MES_ANO",
                "QUINZENA",
            ]
        )

    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["MES_NUM"].map(MESES_PT)
    base["MES_ANO"] = mes_ano_pt(base["DATA"])
    base["QUINZENA"] = base["DATA"].dt.day.apply(identificar_quinzena)
    return base.sort_values("DATA", ascending=False).reset_index(drop=True)


def grafico_barras_top(df_plot: pd.DataFrame, titulo: str):
    fig = go.Figure()
    fig.add_bar(
        x=df_plot["MES_ANO"],
        y=df_plot["RECEITA"],
        name="Receita",
        text=[formato_real(v) for v in df_plot["RECEITA"]],
        textposition="inside",
        marker=dict(color="#10b981", line=dict(color="#5eead4", width=1)),
        hovertemplate="%{x}<br>Receita: %{text}<extra></extra>",
    )
    fig.add_bar(
        x=df_plot["MES_ANO"],
        y=df_plot["DESPESA"],
        name="Despesa",
        text=[formato_real(v) for v in df_plot["DESPESA"]],
        textposition="inside",
        marker=dict(color="#f97316", line=dict(color="#fdba74", width=1)),
        hovertemplate="%{x}<br>Despesa: %{text}<extra></extra>",
    )
    fig.add_bar(
        x=df_plot["MES_ANO"],
        y=df_plot["SALDO"],
        name="Saldo",
        text=[formato_real(v) for v in df_plot["SALDO"]],
        textposition="inside",
        marker=dict(color="#3b82f6", line=dict(color="#93c5fd", width=1)),
        hovertemplate="%{x}<br>Saldo: %{text}<extra></extra>",
    )

    fig.update_layout(
        title=titulo,
        barmode="group",
        height=520,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=52, b=10),
        legend=dict(orientation="h", y=1.08, x=0),
        font=dict(color="#e5eef9"),
        xaxis=dict(title="", tickfont=dict(size=12)),
        yaxis=dict(title="", gridcolor="rgba(255,255,255,.08)", zeroline=False),
        uniformtext_minsize=8,
        uniformtext_mode="hide",
    )
    return fig


def grafico_gastos_mes(df_mes_gastos: pd.DataFrame):
    agrupado = (
        df_mes_gastos.groupby("NOME", as_index=False)["VALOR"]
        .sum()
        .sort_values("VALOR", ascending=False)
        .head(12)
    )
    fig = go.Figure()
    fig.add_bar(
        x=agrupado["NOME"],
        y=agrupado["VALOR"],
        text=[formato_real(v) for v in agrupado["VALOR"]],
        textposition="inside",
        marker=dict(color="#8b5cf6", line=dict(color="#c4b5fd", width=1)),
        hovertemplate="%{x}<br>%{text}<extra></extra>",
    )
    fig.update_layout(
        height=430,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(color="#e5eef9"),
        xaxis=dict(title="", tickangle=-20),
        yaxis=dict(title="", gridcolor="rgba(255,255,255,.08)", zeroline=False),
    )
    return fig


# =========================
# HEADER
# =========================
st.markdown(
    f"""
<div class="hero">
    <h1>💎 Virada Financeira</h1>
    <p>{random.choice(FRASES)}</p>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# LEITURA
# =========================
try:
    df_principal, sheet_names = carregar_planilha(PLANILHA_URL)
except Exception:
    st.error("Erro ao carregar a planilha principal.")
    st.stop()

df = normalizar_colunas(df_principal)
meio = len(df.columns) // 2
receitas = preparar_base(df.iloc[:, :meio].copy())
despesas = preparar_base(df.iloc[:, meio:].copy())

# =========================
# RESUMO GERAL
# =========================
rec_m = (
    receitas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"]
    .sum()
    .rename(columns={"VALOR": "RECEITA"})
)
des_m = (
    despesas.groupby(["ANO", "MES_NUM", "MES"], as_index=False)["VALOR"]
    .sum()
    .rename(columns={"VALOR": "DESPESA"})
)

resumo = pd.merge(rec_m, des_m, on=["ANO", "MES_NUM", "MES"], how="outer").fillna(0)
resumo["SALDO"] = resumo["RECEITA"] - resumo["DESPESA"]
resumo = resumo.sort_values(["ANO", "MES_NUM"]) 
resumo["DATA_CHAVE"] = pd.to_datetime(
    resumo["ANO"].astype(int).astype(str) + "-" + resumo["MES_NUM"].astype(int).astype(str) + "-01"
)
resumo["MES_ANO"] = mes_ano_pt(resumo["DATA_CHAVE"])

# =========================
# INVESTIMENTO
# =========================
try:
    investimento_df = ler_aba(PLANILHA_URL, "INVESTIMENTO")
    valor_investido = limpar_valor(investimento_df.iloc[13, 1])
except Exception:
    valor_investido = 0.0

ano_atual = datetime.now().year
mes_atual = datetime.now().month
resumo_ano = resumo[resumo["ANO"] == ano_atual].copy()

total_receita_ano = resumo_ano["RECEITA"].sum()
total_despesa_ano = resumo_ano["DESPESA"].sum()
saldo_ano = resumo_ano["SALDO"].sum()
saldo_restante = resumo_ano.loc[resumo_ano["MES_NUM"] > mes_atual, "SALDO"].sum()
patrimonio_em_construcao = saldo_restante + valor_investido

# =========================
# GASTOS EXTRAS
# =========================
aba_gastos = detectar_aba_gastos(sheet_names)
if aba_gastos:
    try:
        gastos_df_raw = ler_aba(PLANILHA_URL, aba_gastos)
        gastos = preparar_gastos(gastos_df_raw)
    except Exception:
        gastos = preparar_gastos(pd.DataFrame())
else:
    gastos = preparar_gastos(pd.DataFrame())

# =========================
# KPIS
# =========================
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("💵 Receita no ano", formato_real(total_receita_ano))
c2.metric("💸 Despesa no ano", formato_real(total_despesa_ano))
c3.metric("🏦 Saldo no ano", formato_real(saldo_ano))
c4.metric("🧭 Saldo restante", formato_real(saldo_restante))
c5.metric("📈 Investido", formato_real(valor_investido))
c6.metric("💎 Total em construção", formato_real(patrimonio_em_construcao))

st.markdown('<div class="section-card">', unsafe_allow_html=True)
fig_geral = grafico_barras_top(resumo, "📊 Balanço financeiro geral")
st.plotly_chart(fig_geral, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================
# TABS
# =========================
tab_visao, tab_mes, tab_gastos = st.tabs(
    ["📌 Visão geral", "📅 Mês selecionado", "🧾 Gastos variáveis"]
)

with tab_visao:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📍 Panorama rápido")
    st.markdown(
        f"""
<span class="pill">Ano atual: {ano_atual}</span>
<span class="pill">Próximo foco: {MESES_PT[1 if mes_atual == 12 else mes_atual + 1]}/{ano_atual + 1 if mes_atual == 12 else ano_atual}</span>
<span class="pill">Aba de gastos extras: {aba_gastos if aba_gastos else 'não encontrada'}</span>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.15, 0.85])
    with col1:
        ultimos = resumo.sort_values("DATA_CHAVE", ascending=False).head(6).sort_values("DATA_CHAVE")
        tabela_resumo = ultimos[["MES_ANO", "RECEITA", "DESPESA", "SALDO"]].copy()
        tabela_resumo["RECEITA"] = tabela_resumo["RECEITA"].map(formato_real)
        tabela_resumo["DESPESA"] = tabela_resumo["DESPESA"].map(formato_real)
        tabela_resumo["SALDO"] = tabela_resumo["SALDO"].map(formato_real)
        st.dataframe(
            tabela_resumo.rename(
                columns={
                    "MES_ANO": "Mês",
                    "RECEITA": "Receita",
                    "DESPESA": "Despesa",
                    "SALDO": "Saldo",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    with col2:
        top_despesas = (
            despesas.groupby("DESCRICAO", as_index=False)["VALOR"]
            .sum()
            .sort_values("VALOR", ascending=False)
            .head(8)
        )
        top_despesas["VALOR"] = top_despesas["VALOR"].map(formato_real)
        st.dataframe(
            top_despesas.rename(columns={"DESCRICAO": "Despesa", "VALOR": "Total"}),
            use_container_width=True,
            hide_index=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with tab_mes:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    if mes_atual == 12:
        prox_mes = 1
        prox_ano = ano_atual + 1
    else:
        prox_mes = mes_atual + 1
        prox_ano = ano_atual

    mes_ref = f"{MESES_PT[prox_mes]}/{prox_ano}"
    lista_meses = resumo["MES_ANO"].tolist()
    idx_default = lista_meses.index(mes_ref) if mes_ref in lista_meses else max(len(lista_meses) - 1, 0)
    mes_sel = st.selectbox("📅 Escolha o mês", lista_meses, index=idx_default)

    mes_txt, ano_sel = mes_sel.split("/")
    ano_sel = int(ano_sel)
    num_mes_sel = [k for k, v in MESES_PT.items() if v == mes_txt][0]

    rec_mes = receitas[(receitas["ANO"] == ano_sel) & (receitas["MES_NUM"] == num_mes_sel)].copy()
    des_mes = despesas[(despesas["ANO"] == ano_sel) & (despesas["MES_NUM"] == num_mes_sel)].copy()
    gastos_mes = gastos[(gastos["ANO"] == ano_sel) & (gastos["MES_NUM"] == num_mes_sel)].copy()

    st.subheader(f"📆 Resumo — {mes_sel}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💵 Receitas", formato_real(rec_mes["VALOR"].sum()))
    m2.metric("💸 Despesas fixas", formato_real(des_mes["VALOR"].sum()))
    m3.metric("🧾 Gastos extras", formato_real(gastos_mes["VALOR"].sum()))
    m4.metric(
        "🏦 Saldo líquido",
        formato_real(rec_mes["VALOR"].sum() - des_mes["VALOR"].sum() - gastos_mes["VALOR"].sum()),
    )

    colg1, colg2 = st.columns([1.05, 0.95])
    with colg1:
        if not des_mes.empty:
            despesas_total = (
                des_mes.groupby("DESCRICAO", as_index=False)["VALOR"]
                .sum()
                .sort_values("VALOR", ascending=False)
            )
            fig2 = go.Figure(
                go.Bar(
                    x=despesas_total["DESCRICAO"],
                    y=despesas_total["VALOR"],
                    text=despesas_total["VALOR"].apply(formato_real),
                    textposition="inside",
                    marker=dict(color="#f97316", line=dict(color="#fdba74", width=1)),
                )
            )
            fig2.update_layout(
                title="💸 Despesas fixas do mês",
                height=430,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e5eef9"),
                yaxis=dict(gridcolor="rgba(255,255,255,.08)", zeroline=False),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem despesas fixas neste mês.")
    with colg2:
        if not gastos_mes.empty:
            st.plotly_chart(grafico_gastos_mes(gastos_mes), use_container_width=True)
        else:
            st.info("Sem gastos variáveis neste mês.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab_gastos:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🧾 Controle de gastos variáveis")
    st.caption(
        "Pra vigiar o dinheiro que escapa pelos cantos: extras, impulsos, pequenas fugas e decisões do dia."
    )

    if gastos.empty:
        st.warning(
            "Não encontrei uma aba de gastos variáveis na sua planilha. Crie uma aba chamada GASTOS com colunas como: DATA, MÊS, NOME, FORMA PAGAMENTO, CLASSIFICAÇÃO e VALOR."
        )
        exemplo = pd.DataFrame(
            {
                "DATA": ["02/03/2026", "05/03/2026"],
                "MÊS": ["Mar", "Mar"],
                "NOME": ["BODY SPLASH", "BONE"],
                "FORMA PAGAMENTO": ["PIX", "PIX"],
                "CLASSIFICAÇÃO": ["DISPENSÁVEL", "INDISPENSÁVEL"],
                "VALOR": ["R$ 40,00", "R$ 5,00"],
            }
        )
        st.dataframe(exemplo, use_container_width=True, hide_index=True)
    else:
        lista_meses_gastos = (
            gastos[["ANO", "MES_NUM", "MES_ANO"]]
            .drop_duplicates()
            .sort_values(["ANO", "MES_NUM"], ascending=[False, False])
        )
        opcoes_mes_gastos = lista_meses_gastos["MES_ANO"].tolist()
        mes_padrao_gastos = opcoes_mes_gastos[0] if opcoes_mes_gastos else None

        colf1, colf2 = st.columns([1, 1])
        with colf1:
            mes_filtro = st.selectbox("📆 Mês", opcoes_mes_gastos, index=0 if opcoes_mes_gastos else None)
        with colf2:
            quinzena_filtro = st.selectbox("🌓 Quinzena", ["Todas", "1ª quinzena", "2ª quinzena"], index=0)

        gastos_filtrados = gastos[gastos["MES_ANO"] == mes_filtro].copy() if mes_filtro else gastos.copy()
        if quinzena_filtro != "Todas":
            gastos_filtrados = gastos_filtrados[gastos_filtrados["QUINZENA"] == quinzena_filtro].copy()

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("💸 Total do período", formato_real(gastos_filtrados["VALOR"].sum()))
        g2.metric("🧾 Lançamentos", int(len(gastos_filtrados)))
        g3.metric(
            "🛍️ Dispensável",
            formato_real(
                gastos_filtrados.loc[
                    gastos_filtrados["CLASSIFICACAO"].str.upper() == "DISPENSAVEL", "VALOR"
                ].sum()
            ),
        )
        g4.metric(
            "📌 Indispensável",
            formato_real(
                gastos_filtrados.loc[
                    gastos_filtrados["CLASSIFICACAO"].str.upper() == "INDISPENSAVEL", "VALOR"
                ].sum()
            ),
        )

        colx1, colx2 = st.columns([1.05, 0.95])
        with colx1:
            if not gastos_filtrados.empty:
                por_class = (
                    gastos_filtrados.groupby("CLASSIFICACAO", as_index=False)["VALOR"]
                    .sum()
                    .sort_values("VALOR", ascending=False)
                )
                fig_class = go.Figure(
                    data=[
                        go.Pie(
                            labels=por_class["CLASSIFICACAO"],
                            values=por_class["VALOR"],
                            hole=0.58,
                            text=[formato_real(v) for v in por_class["VALOR"]],
                            textinfo="label+text",
                            marker=dict(colors=["#8b5cf6", "#10b981", "#f97316", "#3b82f6", "#ef4444"]),
                        )
                    ]
                )
                fig_class.update_layout(
                    title="🎯 Onde o dinheiro está escapando",
                    height=430,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e5eef9"),
                    margin=dict(l=10, r=10, t=42, b=10),
                )
                st.plotly_chart(fig_class, use_container_width=True)
            else:
                st.info("Sem lançamentos nesse filtro.")
        with colx2:
            if not gastos_filtrados.empty:
                top_forma = (
                    gastos_filtrados.groupby("FORMA PAGAMENTO", as_index=False)["VALOR"]
                    .sum()
                    .sort_values("VALOR", ascending=False)
                )
                fig_forma = go.Figure(
                    go.Bar(
                        x=top_forma["FORMA PAGAMENTO"],
                        y=top_forma["VALOR"],
                        text=top_forma["VALOR"].apply(formato_real),
                        textposition="inside",
                        marker=dict(color="#06b6d4", line=dict(color="#67e8f9", width=1)),
                    )
                )
                fig_forma.update_layout(
                    title="💳 Forma de pagamento",
                    height=430,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e5eef9"),
                    yaxis=dict(gridcolor="rgba(255,255,255,.08)", zeroline=False),
                    margin=dict(l=10, r=10, t=42, b=10),
                )
                st.plotly_chart(fig_forma, use_container_width=True)
            else:
                st.info("Nada pra mostrar por forma de pagamento.")

        st.markdown("### 📋 Lançamentos do período")
        tabela = gastos_filtrados.copy()
        tabela["DATA"] = tabela["DATA"].dt.strftime("%d/%m/%Y")
        tabela["VALOR"] = tabela["VALOR"].map(formato_real)
        tabela = tabela[
            [
                "DATA",
                "MES",
                "QUINZENA",
                "NOME",
                "FORMA PAGAMENTO",
                "CLASSIFICACAO",
                "VALOR",
            ]
        ].rename(
            columns={
                "MES": "Mês",
                "NOME": "Nome",
                "FORMA PAGAMENTO": "Forma pagamento",
                "CLASSIFICACAO": "Classificação",
            }
        )
        st.dataframe(tabela, use_container_width=True, hide_index=True)

        st.markdown("### 📊 Visão mês a mês")
        visao_mes = (
            gastos.groupby(["ANO", "MES_NUM", "MES_ANO"], as_index=False)["VALOR"]
            .sum()
            .sort_values(["ANO", "MES_NUM"])
        )
        fig_meses = go.Figure(
            go.Bar(
                x=visao_mes["MES_ANO"],
                y=visao_mes["VALOR"],
                text=visao_mes["VALOR"].apply(formato_real),
                textposition="inside",
                marker=dict(color="#22c55e", line=dict(color="#86efac", width=1)),
            )
        )
        fig_meses.update_layout(
            title="🗓️ Evolução dos gastos variáveis",
            height=420,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e5eef9"),
            yaxis=dict(gridcolor="rgba(255,255,255,.08)", zeroline=False),
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_meses, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
