# 📦 Análise de Estoque Fiscaltech

Aplicativo para análise de estoque com base na estrutura de produto e regras de transposição entre armazéns.

## ✅ Funcionalidades

- Upload de arquivos Excel (estrutura e estoque)
- Definição de prefixo de destino (ex: PL)
- Cálculo da necessidade total para produção
- Verificação de saldo no estoque
- Sugestão de transposições entre prefixos permitidos
- Geração de relatório final com download em Excel

## 📂 Como usar

1. Suba este projeto para o GitHub
2. Acesse [streamlit.io](https://streamlit.io/cloud)
3. Conecte ao seu repositório e rode o `app.py`
4. Envie os arquivos `.xlsx` na interface

## 📁 Estrutura esperada dos arquivos

### Estrutura do Produto (Excel)
| Código     | Descricao                        | Quantidade |
|------------|----------------------------------|------------|
| PV0000003  | BLOCO TERMINAL ATERRAMENTO TRI   | 1          |

### Estoque (Excel)
| CODIGO     | TP | ESTOQUE |
|------------|----|---------|
| MP0000003  | MP | 10      |

O código considera o núcleo numérico para identificar componentes (ex: `0000003`).

## 📌 Regras de Transposição

- Permitido entre: PV → PL, MP → PL, AA → PL, etc.
- RP não é permitido como origem ou destino
- Transposições são sugeridas até completar a necessidade
- Se faltar, será informado “Faltando mesmo com transposição”

## ✨ Desenvolvido para a Fiscaltech
