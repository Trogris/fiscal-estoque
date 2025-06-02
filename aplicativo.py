import streamlit as st
import pandas as pd

st.set_page_config(page_title="📦 Análise de Estoque para Produção", layout="wide")

# Custom collapsible menu using a checkbox
with st.container():
    show_menu = st.checkbox("📁 Mostrar opções de entrada", value=True)

if show_menu:
    with st.expander("Upload de Arquivos e Parâmetros", expanded=True):
        estrutura_file = st.file_uploader("📥 Estrutura do Produto", type=["csv", "xlsx"])
        estoque_file = st.file_uploader("📥 Estoque Atual", type=["csv", "xlsx"])

        qtd = st.number_input("Quantidade de Equipamentos a Produzir", min_value=1, step=1)

        codigos = ["PST-10", "PST-20", "PST-30", "PST-42", "PST-50"]
        cod_destino = st.selectbox("Código de Destino", options=codigos)
        entrada_manual = st.text_input("Ou digite um código manualmente")
        if entrada_manual:
            cod_destino = entrada_manual
else:
    estrutura_file = None
    estoque_file = None
    qtd = 0
    cod_destino = ""

st.title("📦 Análise de Estoque para Produção")

if estrutura_file and estoque_file:
    try:
        df_estrutura = pd.read_excel(estrutura_file) if estrutura_file.name.endswith(".xlsx") else pd.read_csv(estrutura_file)
        df_estoque = pd.read_excel(estoque_file) if estoque_file.name.endswith(".xlsx") else pd.read_csv(estoque_file)

        # Regra de transposição (oculta na interface)
        if "Transpor" in df_estrutura.columns:
            df_estrutura = df_estrutura.T.reset_index()
            df_estrutura.columns = df_estrutura.iloc[0]
            df_estrutura = df_estrutura.drop(0)

        st.success("Arquivos carregados com sucesso.")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Prévia – Estrutura")
            st.dataframe(df_estrutura, use_container_width=True)
        with col2:
            st.subheader("Prévia – Estoque")
            st.dataframe(df_estoque, use_container_width=True)

        st.markdown("---")
        st.markdown("### Resultado da Análise")
        # Resultados da lógica interna

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os arquivos: {e}")
else:
    st.info("Envie os dois arquivos para iniciar.")
