import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Análise de Estoque para Produção", layout="wide")

st.markdown("<h1 style='display: flex; align-items: center;'>"
            "<img src='https://cdn-icons-png.flaticon.com/512/4290/4290854.png' width='40' style='margin-right: 10px'>"
            "Análise de Estoque para Produção</h1>", unsafe_allow_html=True)

estrutura_file = st.file_uploader("📥 Estrutura do Produto", type=["csv", "xlsx"])
estoque_file = st.file_uploader("📥 Estoque Atual", type=["csv", "xlsx"])

col1, col2 = st.columns(2)
with col1:
    qtd = st.number_input("Quantidade de Equipamentos a Produzir", min_value=1, step=1)
with col2:
    cod_destino = st.text_input("Código de Destino")

if estrutura_file and estoque_file:
    try:
        df_estrutura = pd.read_excel(estrutura_file) if estrutura_file.name.endswith(".xlsx") else pd.read_csv(estrutura_file)
        df_estoque = pd.read_excel(estoque_file) if estoque_file.name.endswith(".xlsx") else pd.read_csv(estoque_file)

        # Regra de transposição (aplicada silenciosamente)
        if "Transpor" in df_estrutura.columns:
            df_estrutura = df_estrutura.T.reset_index()
            df_estrutura.columns = df_estrutura.iloc[0]
            df_estrutura = df_estrutura.drop(0)

        st.success("Arquivos carregados com sucesso.")

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Prévia – Estrutura")
            st.dataframe(df_estrutura, use_container_width=True)
        with col4:
            st.subheader("Prévia – Estoque")
            st.dataframe(df_estoque, use_container_width=True)

        st.markdown("---")
        st.markdown("### Resultado da Análise")
        # Aqui entram os cálculos e regras da produção

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os arquivos: {e}")
else:
    st.info("Envie os dois arquivos para iniciar.")
