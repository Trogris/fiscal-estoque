
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Análise de Estoque para Produção", layout="wide")

st.title("📦 Análise de Estoque para Produção")
st.markdown("Versão R11 – Regras atualizadas com uso direto de RP para PL e transposição por prioridade")

# Uploads
col1, col2, col3 = st.columns(3)
with col1:
    estrutura_file = st.file_uploader("📂 Estrutura do Produto (.xlsx)", type="xlsx", key="estrutura")
with col2:
    estoque_file = st.file_uploader("📂 Estoque Atual (.xlsx)", type="xlsx", key="estoque")
with col3:
    quantidade = st.number_input("🔢 Quantidade de Equipamentos a Produzir", min_value=1, value=1)

# Código destino (PL ou PV)
codigo_destino = st.selectbox("🏷️ Prefixo do Código de Destino", options=["PL", "PV"])

executar = st.button("🚀 Executar Análise")

if executar and estrutura_file and estoque_file:
    estrutura_df = pd.read_excel(estrutura_file)
    estoque_df = pd.read_excel(estoque_file)

    estrutura_df["Quantidade Total Necessária"] = estrutura_df["Quantidade necessária"] * quantidade

    # Extrai prefixo do estoque
    estoque_df["Prefixo"] = estoque_df["Código do Item"].str.extract(r'^([A-Z]+)')

    resultado = []

    for _, item in estrutura_df.iterrows():
        codigo_item = item["Código do Item"]
        descricao_item = item["Descrição do Item"]
        qtd_necessaria = item["Quantidade Total Necessária"]

        saldo_disponivel = estoque_df[estoque_df["Código do Item"] == codigo_item]
        saldo_destino = saldo_disponivel[saldo_disponivel["Prefixo"] == codigo_destino]["Saldo"].sum()

        transposicoes = saldo_disponivel[
            (saldo_disponivel["Prefixo"].isin(["AA", "MP", "PV", "PL"])) &
            (saldo_disponivel["Prefixo"] != codigo_destino) &
            (saldo_disponivel["Prefixo"] != "RP")
        ]

        saldo_transponivel = transposicoes["Saldo"].sum()

        saldo_rp = saldo_disponivel[saldo_disponivel["Prefixo"] == "RP"]["Saldo"].sum() if codigo_destino == "PL" else 0

        saldo_total = saldo_destino + saldo_transponivel + saldo_rp
        faltante = max(0, qtd_necessaria - saldo_total)

        usar_destino = min(saldo_destino, qtd_necessaria)
        restante = qtd_necessaria - usar_destino

        usar_transposicao = min(saldo_transponivel, restante)
        restante -= usar_transposicao

        usar_rp = min(saldo_rp, restante) if codigo_destino == "PL" else 0
        restante -= usar_rp

        transpor_texto = f"{usar_transposicao} unidades transpostas" if usar_transposicao else ""
        rp_texto = f"{usar_rp} unidades de RP usadas" if usar_rp else ""
        comentario = " | ".join(filter(None, [transpor_texto, rp_texto]))
        if restante > 0:
            comentario += f" | {restante} a comprar"

        resultado.append({
            "Código do Item": codigo_item,
            "Descrição do Item": descricao_item,
            "Qtd. Necessária": qtd_necessaria,
            "No Destino": usar_destino,
            "Transposição": usar_transposicao,
            "Uso RP": usar_rp,
            "Faltante": restante,
            "🔧 Parâmetros da Análise": comentario
        })

    df_resultado = pd.DataFrame(resultado)

    st.success("✅ Análise concluída com sucesso!")
    st.dataframe(df_resultado, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_resultado.to_excel(writer, index=False)
    st.download_button("📥 Baixar Resultado em Excel", data=buffer.getvalue(), file_name="resultado_estoque.xlsx")

if st.button("🔄 Nova Análise"):
    st.experimental_rerun()
