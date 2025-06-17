# Painel Gratificação SUS

Este painel foi desenvolvido em Python utilizando Streamlit e carrega dados diretamente de uma planilha do Google Sheets.

## 🔗 Acesso aos Dados
Os dados são provenientes da planilha pública:  
[Planilha Gratificação SUS](https://docs.google.com/spreadsheets/d/1MpjevwLmc4w0OF4ffZEaOhd5hLWaH6FL/edit?usp=sharing)

## 🚀 Funcionalidades
- Filtros por **Mês** e **Indicador**
- Visualização de resumo dos indicadores
- Avaliação automática se a **meta foi ou não alcançada**
- Apresentação diferenciada do **Indicador 3**, que não é padronizado por mês
- Download dos dados filtrados em formato Excel (.xlsx)

## 🛠️ Instalação local

Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
Instale as dependências:

bash
Copiar
Editar
pip install -r requirements.txt
Execute o painel:

bash
Copiar
Editar
streamlit run grafis.py
☁️ Deploy na Nuvem
O painel é compatível com Streamlit Cloud.
Basta conectar este repositório ao Streamlit Cloud e ele será executado automaticamente.

📑 Observações
O painel lê diretamente a aba GERAL da planilha.

Se desejar adicionar novos indicadores ou meses, basta atualizar a planilha no Google Sheets.

Desenvolvido com ❤️ e 🐍 por [Vigilância em Saúde Ipojuca].