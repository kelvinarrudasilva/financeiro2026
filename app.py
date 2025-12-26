st.subheader("📌 Composição do mês")

col_r, col_d = st.columns(2)

with col_r:
    if not rec_mes.empty:
        fig_r = px.pie(
            rec_mes,
            values="VALOR",
            names="DESCRICAO",
            hole=0.5,
            title="💰 Receitas"
        )
        fig_r.update_traces(
            texttemplate="R$ %{value:,.2f}",
            textposition="inside"
        )
        fig_r.update_layout(
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=True
        )
        st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.info("Nenhuma receita registrada neste mês.")

with col_d:
    if not des_mes.empty:
        fig_d = px.pie(
            des_mes,
            values="VALOR",
            names="DESCRICAO",
            hole=0.5,
            title="💸 Despesas"
        )
        fig_d.update_traces(
            texttemplate="R$ %{value:,.2f}",
            textposition="inside"
        )
        fig_d.update_layout(
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=True
        )
        st.plotly_chart(fig_d, use_container_width=True)
    else:
        st.info("Nenhuma despesa registrada neste mês.")
