import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Painel Gratificação SUS", layout="wide")
st.title("Painel de Indicadores - Gratificação SUS")

# Função para carregar os dados
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1MpjevwLmc4w0OF4ffZEaOhd5hLWaH6FL/export?format=csv&gid=793227745"
    df = pd.read_csv(url)
    return df

df = load_data()

# Limpeza de dados (exemplo considerando a estrutura da imagem)
df.columns = df.columns.str.strip().str.lower()
df = df.rename(columns={'indicador/mês': 'indicador'})

# Separando os indicadores
indicadores = df['indicador'].dropna().unique()

# Filtros
st.sidebar.header("Filtros")
indicador_selecionado = st.sidebar.selectbox("Selecione o indicador", indicadores)

# Verifica se o indicador é mensal ou por ciclo
if indicador_selecionado == 'Proporção de casos de doenças de notificação compulsória imediata nacional (DNCI) encerrados em até 60 (sessenta) dias após notificação.':
    tipo = 'mensal'
elif indicador_selecionado == 'Proporção de preenchimento dos campos “Ocupação” e “Atividade Econômica (CNAE)” nas notificações de acidente de trabalho, acidente de trabalho com exposição a material biológico e intoxicação exógena segundo município de notificação.':
    tipo = 'mensal'
elif indicador_selecionado == 'Realizar a primeira inspeção para emissão de licença sanitária de alto risco em 30 dias a partir do recebimento do processo pela REDESIM.':
    tipo = 'mensal'
else:
    tipo = 'ciclo'

# Filtrando dados
if tipo == 'mensal':
    meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    df_filtrado = df[df['indicador'] == indicador_selecionado][['indicador'] + meses + ['meta']]
else:
    ciclos = ['1º ciclo', '2º ciclo', '3º ciclo', '4º ciclo']
    df_filtrado = df[df['indicador'] == indicador_selecionado][['indicador'] + ciclos + ['meta']]

st.subheader("Resumo da Seleção")
st.dataframe(df_filtrado)

# Verificação de Meta
meta = df_filtrado['meta'].values[0] if not df_filtrado['meta'].isnull().all() else 'Não informada'
st.info(f"Meta para este indicador: {meta}")

# Download dos dados
@st.cache_data
def convert_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Indicadores')
    processed_data = output.getvalue()
    return processed_data

st.download_button(
    label="📥 Baixar tabela em Excel",
    data=convert_df(df_filtrado),
    file_name='dados_indicadores.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

st.caption("Fonte: Planilha Gratificação SUS")