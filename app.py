# =========================
# BASES
# =========================

# Garantir que a planilha tenha colunas suficientes
if df.shape[1] < 10:
    st.error(f"A planilha retornou apenas {df.shape[1]} colunas. Verifique a estrutura.")
    st.write("Colunas encontradas:", df.columns)
    st.stop()

# RECEITAS
receitas = df.iloc[1:, 1:5].copy()

if receitas.shape[1] >= 4:
    receitas = receitas.iloc[:, :4]
    receitas.columns = ["DATA","MES","DESCRICAO","VALOR"]
else:
    st.error(f"Erro nas RECEITAS: esperado 4 colunas, encontrado {receitas.shape[1]}")
    st.stop()

# DESPESAS
despesas = df.iloc[1:, 6:10].copy()

if despesas.shape[1] >= 4:
    despesas = despesas.iloc[:, :4]
    despesas.columns = ["DATA","MES","DESCRICAO","VALOR"]
else:
    st.error(f"Erro nas DESPESAS: esperado 4 colunas, encontrado {despesas.shape[1]}")
    st.stop()

# Tratamento padrão
for base in [receitas, despesas]:
    base["VALOR"] = base["VALOR"].apply(limpar_valor)
    base["DATA"] = pd.to_datetime(base["DATA"], errors="coerce")
    base.dropna(subset=["DATA"], inplace=True)
    base["ANO"] = base["DATA"].dt.year
    base["MES_NUM"] = base["DATA"].dt.month
    base["MES"] = base["DATA"].dt.strftime("%b").str.lower()
