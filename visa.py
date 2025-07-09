import streamlit as st
import pandas as pd
import calendar
from io import BytesIO
from datetime import datetime

# 🎨 Configuração da página
st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("📋 Indicador da Vigilância Sanitária — Mensal")

# -------------------------------
# 📥 Fonte de dados
# -------------------------------
url = (
    'https://docs.google.com/spreadsheets/d/'
    '1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak'
    '/export?format=csv&gid=502962216'
)

@st.cache_data
def carregar_dados():
    df = pd.read_csv(url, dtype=str)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Exibir colunas disponíveis para debug
    st.write("Colunas disponíveis no sheet:", list(df.columns))

    # Mapeamento esperado de colunas
    expected = {
        'DATA_CAPTACAO': 'ENTRADA',           # Coluna F: data de captação
        'DATA_INSPECAO': '1ª INSPEÇÃO',       # Coluna J: primeira inspeção
        'DATA_CONCLUSAO': 'DATA CONCLUSÃO',   # Coluna N: conclusão
        'CLASS_RISCO': 'CLASSIFICAÇÃO DE RISCO'  # Coluna G: risco
    }

    # Verificar presença das colunas esperadas
    for key, name in expected.items():
        if name not in df.columns:
            st.error(f"Coluna esperada '{name}' não encontrada. Disponíveis: {list(df.columns)}")
            st.stop()

    # Converter datas
    df['DATA_CAPTACAO'] = pd.to_datetime(df[expected['DATA_CAPTACAO']], dayfirst=True, errors='coerce')
    df['DATA_INSPECAO'] = pd.to_datetime(df[expected['DATA_INSPECAO']], dayfirst=True, errors='coerce')
    df['DATA_CONCLUSAO'] = pd.to_datetime(df[expected['DATA_CONCLUSAO']], dayfirst=True, errors='coerce')

    # Padronizar coluna de risco
    df['CLASS_RISCO'] = df[expected['CLASS_RISCO']].str.title()

    return df

# Carregar dados
df = carregar_dados()

# -------------------------------
# 🛠️ Filtros
# -------------------------------
st.sidebar.header("Filtros")

risco = st.sidebar.selectbox(
    "🎯 Estratificação de Risco",
    sorted(df['CLASS_RISCO'].dropna().unique())
)

indicador = st.sidebar.selectbox(
    "📊 Indicador",
    [
        "Inspeções realizadas em até 30 dias após a captação do processo",
        "Processos finalizados em até 90 dias após a captação do processo"
    ]
)

periodo = st.sidebar.date_input(
    "⏳ Selecionar mês/ano",
    value=datetime(datetime.now().year, datetime.now().month, 1),
    min_value=df['DATA_CAPTACAO'].min().replace(day=1),
    max_value=datetime(datetime.now().year, datetime.now().month, 1),
    help="Escolha o primeiro dia do mês desejado"
)
ano_sel = periodo.year
nmes_sel = periodo.month

# -------------------------------
# 🔍 Filtrar dados
# -------------------------------
df_risco = df[df['CLASS_RISCO'] == risco]
df_risco['ANO'] = df_risco['DATA_CAPTACAO'].dt.year
df_risco['MES'] = df_risco['DATA_CAPTACAO'].dt.month

df_sel = df_risco[(df_risco['ANO'] == ano_sel) & (df_risco['MES'] == mes_sel)]

# -------------------------------
# ⚙️ Cálculo do Indicador
# -------------------------------
def calcula_indicador(grp, tipo):
    total = len(grp)
    if tipo.startswith("Inspeções"):
        mask = (grp['DATA_INSPECAO'] - grp['DATA_CAPTACAO']).dt.days <= 30
    else:
        mask = (grp['DATA_CONCLUSAO'] - grp['DATA_CAPTACAO']).dt.days <= 90
    cumpriram = int(mask.sum())
    pct = (cumpriram / total * 100) if total > 0 else 0
    return pd.Series({
        'Entradas': total,
        'Cumpriram': cumpriram,
        '%': f"{pct:.0f}%",
        'Meta': '80%'
    })

# Agrupar e aplicar cálculo
grupo = df_sel.groupby(['ANO', 'MES'])
tabela = grupo.apply(lambda g: calcula_indicador(g, indicador)).reset_index()

tabela['Mês-Ano'] = tabela.apply(
    lambda row: f"{calendar.month_name[row['MES']]} {row['ANO']}", axis=1
)

tabela = tabela[['Mês-Ano', 'Entradas', 'Cumpriram', '%', 'Meta']]

# -------------------------------
# 📋 Exibição
# -------------------------------
st.table(tabela)

# -------------------------------
# 📥 Download
# -------------------------------
def gerar_excel(df_excel):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_excel.to_excel(writer, index=False, sheet_name='Indicadores')
    return output.getvalue()

st.download_button(
    label="📥 Download Excel",
    data=gerar_excel(tabela),
    file_name=f"indicadores_{nmes_sel}_{ano_sel}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"