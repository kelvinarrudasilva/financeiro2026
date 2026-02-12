# =========================
# SALDO RESTANTE ATÉ O FINAL DO ANO
# =========================

ano_atual = datetime.now().year
mes_atual = datetime.now().month

resumo_ano_atual = resumo[resumo["ANO"] == ano_atual]

saldo_restante = resumo_ano_atual[
    resumo_ano_atual["MES_NUM"] >= mes_atual
]["SALDO"].sum()

mes_inicio_txt = datetime(ano_atual, mes_atual, 1).strftime("%b").capitalize()
mes_fim_txt = "Dez"

st.markdown(
    f"""
    <div style='
        background: linear-gradient(145deg, #16161d, #1b1b24);
        padding:18px;
        border-radius:16px;
        border:1px solid #1f1f2b;
        margin-top:10px;
        text-align:center;
    '>
        <div style='font-size:14px; color:#9ca3af;'>
            Saldo Restante <span style='font-size:12px;'>( {mes_inicio_txt}. a {mes_fim_txt}. )</span>
        </div>
        <div style='font-size:26px; font-weight:600; margin-top:5px;'>
            {formato_real(saldo_restante)}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
