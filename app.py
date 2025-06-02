import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Análise de Estoque para Produção", layout="wide")

st.title("📦 Análise de Estoque para Produção")

# Upload dos arquivos
estrutura_file = st.file_uploader("📥 Estrutura do Produto", type=["xlsx", "csv"])
estoque_file = st.file_uploader("📥 Estoque Atual", type=["xlsx", "csv"])

# Entrada de parâmetros
col1, col2 = st.columns(2)
with col1:
    qtd_equipamentos = st.number_input("Quantidade de Equipamentos a Produzir", min_value=1, step=1)
with col2:
    destino = st.text_input("Código de Destino").strip().upper()

def carregar_arquivo(arquivo):
    if arquivo.name.endswith('.csv'):
        return pd.read_csv(arquivo, sep=None, engine='python')
    return pd.read_excel(arquivo)

def analisar_estoque(estrutura_df, estoque_df, qtd_equipamentos, destino):
    estrutura_df.columns = estrutura_df.columns.str.strip()
    estoque_df.columns = estoque_df.columns.str.strip()

    estrutura_df["Código do Item"] = estrutura_df["Código do Item"].astype(str).str.strip().str.upper()
    estoque_df["Código do Item"] = estoque_df["Código do Item"].astype(str).str.strip().str.upper()
    estoque_df["Prefixo"] = estoque_df["Prefixo"].astype(str).str.strip().str.upper()

    estrutura_df["Quantidade Total Necessária"] = estrutura_df["Quantidade"] * qtd_equipamentos

    resultado = []

    for _, row in estrutura_df.iterrows():
        item = row["Código do Item"]
        descricao = row["Descrição do Item"]
        qtd_necessaria = row["Quantidade Total Necessária"]

        estoque_destino = estoque_df[(estoque_df["Código do Item"] == item) & (estoque_df["Prefixo"] == destino)]["Saldo"].sum()

        falta = max(qtd_necessaria - estoque_destino, 0)

        transposicao_sugerida = 0
        origem_transposicao = ""

        if falta > 0:
            if destino == "PL":
                estoque_rp = estoque_df[(estoque_df["Código do Item"] == item) & (estoque_df["Prefixo"] == "RP")]["Saldo"].sum()
                if estoque_rp > 0:
                    usar_rp = min(falta, estoque_rp)
                    falta -= usar_rp
                    origem_transposicao += f"Usar {usar_rp} do RP. "
                    transposicao_sugerida += usar_rp

            saldo_outros = estoque_df[
                (estoque_df["Código do Item"] == item) &
                (estoque_df["Prefixo"] != destino) &
                (estoque_df["Prefixo"] != "RP")
            ].groupby("Prefixo")["Saldo"].sum()

            for prefixo_origem, saldo in saldo_outros.items():
                if saldo > 0 and falta > 0:
                    qtd_transp = min(saldo, falta)
                    falta -= qtd_transp
                    origem_transposicao += f"Transpor {qtd_transp} de {prefixo_origem} para {destino}. "
                    transposicao_sugerida += qtd_transp

        resultado.append({
            "Código do Item": item,
            "Descrição": descricao,
            "Qtd. Necessária": qtd_necessaria,
            "Saldo em Estoque do Destino": estoque_destino,
            "Falta": max(qtd_necessaria - estoque_destino, 0),
            "Necessário Transposição": transposicao_sugerida,
            "📋 Ações Sugeridas": origem_transposicao.strip(),
            "🔧 Parâmetros da Análise": f"{qtd_equipamentos} un. | Destino: {destino}"
        })

    return pd.DataFrame(resultado)

if estrutura_file and estoque_file and qtd_equipamentos > 0 and destino:
    estrutura_df = carregar_arquivo(estrutura_file)
    estoque_df = carregar_arquivo(estoque_file)

    df_resultado = analisar_estoque(estrutura_df, estoque_df, qtd_equipamentos, destino)

    st.dataframe(df_resultado, use_container_width=True)

    buffer = io.BytesIO()
    df_resultado.to_excel(buffer, index=False, engine='openpyxl')
    st.download_button("Baixar Resultado em Excel", data=buffer.getvalue(), file_name="resultado_estoque.xlsx")
