
# 📦 Análise de Estoque para Produção

Aplicativo desenvolvido em Streamlit para validar a disponibilidade de componentes em estoque com base em uma estrutura de produto, considerando regras de transposição e uso de itens reparados.

## Funcionalidades

- Upload de arquivos de estrutura e estoque (.xlsx ou .csv)
- Definição do código de destino (ex: PL, PV, etc.)
- Cálculo de necessidade total de itens para produção
- Sugestão de uso de estoque existente e transposição entre prefixos
- Geração de relatório final em Excel

## Regras de Negócio

- Preferência por estoque no prefixo de destino
- Pode usar itens do RP apenas se o destino for PL
- RP não pode ser usado para produtos de venda
- Transposição sugerida entre prefixos permitidos conforme as regras

