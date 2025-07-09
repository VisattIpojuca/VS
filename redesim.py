import streamlit as st
import pandas as pd
import calendar
from io import BytesIO
from datetime import datetime

# Configuração
st.set_page_config(page_title="Painel Mensal VISA", layout="wide")
st.title("📋 Indicadores Mensais - Vigilância Sanitária de Ipojuca")

# Fonte de dados
@st.cache_data
def carregar_dados():
    url = (
        "https://docs.google.com/spreadsheets/d/"
        "1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv&gid=502962216"
    )
    df = pd.read_csv(url)
    # converter datas
    df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], dayfirst=True, errors='coerce')
    df['1ª INSPEÇÃO'] = pd.to_datetime(df['1ª INSPEÇÃO'], dayfirst=True, errors='coerce')
    df['DATA CONCLUSÃO'] = pd.to_datetime(df['DATA CONCLUSÃO'], dayfirst=True, errors='coerce')
    return df

df = carregar_dados()

# --- Filtros ---
st.sidebar.header("Filtros")

# 1: Estratificação de Risco
risco_opts = ["Baixo Risco", "Médio Risco", "Alto Risco"]
risco = st.sidebar.selectbox("🎯 Estratificação de Risco", risco_opts)

# 2: Indicador
indic_opts = [
    "Inspeções realizadas em até 30 dias após a captação do processo",
    "Processos finalizados em até 90 dias após a captação do processo"
]
indicador = st.sidebar.selectbox("📊 Indicador", indic_opts)

# 3: Mês/Ano
mes_ano = st.sidebar.date_input(
    "⏳ Selecionar Mês/Ano", 
    value=datetime(datetime.now().year, datetime.now().month, 1),
    min_value=datetime(2020,1,1).replace(day=1),
    max_value=datetime(datetime.now().year, datetime.now().month,1)
)
ano_sel, mes_sel = mes_ano.year, mes_ano.month

# Filtrar por risco (coluna CLASSIFICAÇÃO DE RISCO existe no sheet original)
df = df[df['CLASSIFICAÇÃO DE RISCO'].str.title() == risco]

# Extrair campo ano/mês
df['ANO'] = df['ENTRADA'].dt.year
df['MES'] = df['ENTRADA'].dt.month

df_sel = df[(df['ANO']==ano_sel)&(df['MES']==mes_sel)]

# Agrupar e calcular

def calcula(grp):
    total = len(grp)
    if indicador.startswith("Inspeções"):
        mask = (grp['1ª INSPEÇÃO'] - grp['ENTRADA']).dt.days <= 30
    else:
        mask = (grp['DATA CONCLUSÃO'] - grp['ENTRADA']).dt.days <= 90
    ok = int(mask.sum())
    pct = (ok/total*100) if total>0 else 0
    return pd.Series({'Entradas': total, 'Cumpriram': ok, '%': f"{pct:.0f}%", 'Meta': '80%'})

tab = df_sel.groupby(['ANO','MES']).apply(calcula).reset_index()
tab['Mês-Ano'] = tab.apply(lambda r: f"{calendar.month_name[r['MES']]} {r['ANO']}", axis=1)
tabela = tab[['Mês-Ano','Entradas','Cumpriram','%','Meta']]

# Exibir tabela
st.table(tabela)

# Download Excel

def to_excel(df):
    out = BytesIO()
    with pd.ExcelWriter(out, engine='xlsxwriter') as w:
        df.to_excel(w, index=False, sheet_name='Indicadores')
    return out.getvalue()

st.download_button(
    "📥 Download Excel",
    data=to_excel(tabela),
    file_name=f"indicadores_{mes_sel}_{ano_sel}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)