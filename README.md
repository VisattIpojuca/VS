# 🦠 Painel de Indicadores da Vigilância Sanitária de Ipojuca

Este repositório contém o painel de indicadores mensais da Vigilância Sanitária de Ipojuca, publicado no Streamlit.

## 🔗 Acesse o painel online:
👉 [Painel VISA no Streamlit](https://painelvisa.streamlit.app/)

---

## 🚀 Funcionalidades Principais

- 🎯 Filtragem por Estratificação de Risco (Baixo, Médio, Alto)
- 📊 Seleção de Indicador:
  - Inspeções realizadas em até 30 dias após captação do processo
  - Processos finalizados em até 90 dias após captação do processo
- ⏳ Seleção de mês/ano para visualização
- 📋 Tabela consolidada de indicadores mês a mês:
  - Entradas
  - Cumprimentos do indicador
  - Percentual de cumprimento
  - Meta fixa (80%)
- 📥 Download dos dados em Excel

---

## 📦 Como executar localmente

1. Clone este repositório:
   ```bash
   git clone https://github.com/seuusuario/painel-visa-indicadores.git
   cd painel-visa-indicadores

 2. Instale as dependências:
 pip install -r requirements.txt

 3. Rode o Streamlit:
 streamlit run visa.py