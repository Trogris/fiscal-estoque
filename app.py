
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Análise de Estoque Fiscaltech", layout="wide")

st.title("📦 Análise de Estoque para Produção")

st.markdown("### 1. Upload dos Arquivos")
estoque_file = st.file_uploader("📁 Envie o arquivo de estoque (.xlsx)", type="xlsx", key="estoque")
estrutura_file = st.file_uploader("📁 Envie o arquivo de estrutura do produto (.xlsx)", type="xlsx", key="estrutura")
qtd_equipamentos = st.number_input("🔢 Quantidade de equipamentos a produzir", min_value=1, step=1)
codigo_destino = st.selectbox("🏷️ Prefixo do código de destino", ["PL", "PV", "MP", "AA"])

if estoque_file and estrutura_file and qtd_equipamentos > 0:
    estoque_df = pd.read_excel(estoque_file)
    estrutura_df = pd.read_excel(estrutura_file)

    # Padronizar estrutura
    estrutura_df.columns = ['componente', 'descricao', 'qtd_por_equipamento']
    estrutura_df['qtd_necessaria'] = estrutura_df['qtd_por_equipamento'] * qtd_equipamentos

    # Padronizar estoque
    estoque_df = estoque_df.rename(columns={"CODIGO": "componente", "TP": "codigo", "ESTOQUE": "qtd"})
    estoque_df['codigo'] = estoque_df['codigo'].str.upper()

    # Regras fixas
    regras_df = pd.DataFrame({
        "codigo_origem": ["PV", "PV", "AA", "AA", "MP", "MP", "PL", "PL"],
        "codigo_destino": ["PL", "MP", "PV", "MP", "PL", "PV", "MP", "PV"]
    })
    regras_validas = regras_df[~regras_df['codigo_origem'].str.startswith("RP") & ~regras_df['codigo_destino'].str.startswith("RP")]

    # Análise
    resultado = []
    for _, item in estrutura_df.iterrows():
        comp = item['componente']
        qtd_necessaria = item['qtd_necessaria']
        est_ok = estoque_df[(estoque_df['componente'] == comp) & (estoque_df['codigo'] == codigo_destino)]
        qtd_ok = est_ok['qtd'].sum()

        if qtd_ok >= qtd_necessaria:
            resultado.append((comp, 'OK', 0, '-'))
        else:
            faltante = qtd_necessaria - qtd_ok
            transposicoes = []
            qtd_restante = faltante
            alt_origens = regras_validas[regras_validas['codigo_destino'] == codigo_destino]['codigo_origem'].unique().tolist()
            for cod in alt_origens:
                est_alt = estoque_df[(estoque_df['componente'] == comp) & (estoque_df['codigo'] == cod)]
                qtd_alt = est_alt['qtd'].sum()
                if qtd_alt > 0:
                    usar = min(qtd_alt, qtd_restante)
                    transposicoes.append(f"{usar} unidades do {cod} para {codigo_destino}")
                    qtd_restante -= usar
                if qtd_restante <= 0:
                    break

            if qtd_restante <= 0:
                resultado.append((comp, 'Necessário Transposição', faltante, ' / '.join(transposicoes)))
            else:
                resultado.append((comp, 'Faltando mesmo com transposição', qtd_restante, ' / '.join(transposicoes) if transposicoes else '-'))

    df_resultado = pd.DataFrame(resultado, columns=['Componente', 'Situação', 'Qtd Faltante', 'Transposição Sugerida'])

    st.markdown("### ✅ Resultado da Análise")
    st.dataframe(df_resultado, use_container_width=True)
    st.download_button("📥 Baixar Resultado em Excel", data=df_resultado.to_excel(index=False), file_name="resultado_estoque.xlsx")
