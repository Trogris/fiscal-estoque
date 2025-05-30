
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Análise de Estoque Fiscaltech", layout="wide")
st.title("📦 Análise de Estoque para Produção")

with st.sidebar:
    st.markdown("<style>div[data-testid='stSidebar'] {width: 300px;}</style>", unsafe_allow_html=True)
    st.header("🔧 Parâmetros da Análise")
    qtd_equipamentos = st.number_input("Quantidade de Equipamentos a Produzir", min_value=1, value=5)
    codigo_destino = st.selectbox("Prefixo de Código de Destino (TP)", ["PL", "PV", "MP", "AA"])

st.markdown("---")

estrutura_file = st.file_uploader("📥 Envie a planilha de Estrutura do Produto", type=["xlsx"])
estoque_file = st.file_uploader("📥 Envie a planilha de Estoque Atual", type=["xlsx"])

executar = st.button("🚀 Executar Análise")
nova_analise = st.button("🔁 Nova Análise")
if nova_analise:
    st.rerun()

if executar and estrutura_file and estoque_file:
    estrutura_df = pd.read_excel(estrutura_file)
    estoque_df = pd.read_excel(estoque_file)

    def extrair_nucleo(codigo):
        return ''.join(filter(str.isdigit, str(codigo)))

    estoque_df['nucleo'] = estoque_df['CODIGO'].apply(extrair_nucleo)
    estoque_df['TP'] = estoque_df['TP'].str.upper()
    estoque_df = estoque_df.rename(columns={"ESTOQUE": "qtd"})

    estrutura_df['nucleo'] = estrutura_df['Código'].apply(extrair_nucleo)
    estrutura_df = estrutura_df.rename(columns={"Quantidade": "qtd_por_equipamento"})
    estrutura_df['qtd_necessaria'] = estrutura_df['qtd_por_equipamento'] * qtd_equipamentos

    regras_df = pd.DataFrame({
        "codigo_origem": ["PV", "PV", "AA", "AA", "MP", "MP", "PL", "PL"],
        "codigo_destino": ["PL", "MP", "PV", "MP", "PL", "PV", "MP", "PV"]
    })

    regras_validas = regras_df[
        ~regras_df['codigo_origem'].str.startswith("RP") &
        ~regras_df['codigo_destino'].str.startswith("RP")
    ]

    resultado = []
    for _, item in estrutura_df.iterrows():
        nucleo = item['nucleo']
        qtd_necessaria = item['qtd_necessaria']
        est_ok = estoque_df[(estoque_df['nucleo'] == nucleo) & (estoque_df['TP'] == codigo_destino)]
        qtd_ok = est_ok['qtd'].sum()

        if qtd_ok >= qtd_necessaria:
            resultado.append((item['Código'], item['Descricao'], 'OK', 0, '-'))
        else:
            faltante = qtd_necessaria - qtd_ok
            transposicoes = []
            qtd_restante = faltante
            alt_origens = regras_validas[regras_validas['codigo_destino'] == codigo_destino]['codigo_origem'].unique().tolist()
            for cod in alt_origens:
                est_alt = estoque_df[(estoque_df['nucleo'] == nucleo) & (estoque_df['TP'] == cod)]
                qtd_alt = est_alt['qtd'].sum()
                if qtd_alt > 0:
                    usar = min(qtd_alt, qtd_restante)
                    transposicoes.append(f"{usar} unidades do {cod} para {codigo_destino}")
                    qtd_restante -= usar
                if qtd_restante <= 0:
                    break

            if faltante > 0 and not transposicoes:
                status = 'Faltando mesmo com transposição'
            else:
                status = 'Necessário Transposição' if qtd_restante <= 0 else 'Faltando mesmo com transposição'
            resultado.append((item['Código'], item['Descricao'], status, qtd_restante if qtd_restante > 0 else 0, ' / '.join(transposicoes) if transposicoes else '-'))

    df_resultado = pd.DataFrame(resultado, columns=['Componente', 'Descrição', 'Situação', 'Qtd Faltante', 'Transposição Sugerida'])

    st.success("✅ Análise concluída com sucesso!")
    st.dataframe(df_resultado, use_container_width=True)

    buffer = BytesIO()
    df_resultado.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    st.download_button(
        label="📥 Baixar Resultado em Excel",
        data=buffer,
        file_name="resultado_estoque.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
