import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# ---🔐 LOGIN SIMPLES ---
def login():
    st.title("🔐 Painel de Indicadores da VISA de Ipojuca")
    st.subheader("Acesso Restrito")
    with st.form("login_form"):
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar")
    if submit:
        if username == "admin" and password == "Ipojuca@2025*":
            st.session_state["autenticado"] = True
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Indicadores VISA Ipojuca", layout="wide")
st.title("📊 Indicadores VISA - Tabela por Mês")

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv"
    df = pd.read_csv(url)

    df.rename(columns={
        'NOME': 'ESTABELECIMENTO',
        'CONCLUSÃO': 'SITUAÇÃO',
        'DATA CONCLUSÃO': 'DATA_CONCLUSAO',
        'PREV 1ª INSP': 'PREVISAO_1A_INSP',
        'Numerador 1': 'NUMERADOR_1'
    }, inplace=True)

    df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
    df['1ª INSPEÇÃO'] = pd.to_datetime(df['1ª INSPEÇÃO'], errors='coerce')
    df['DATA_CONCLUSAO'] = pd.to_datetime(df['DATA_CONCLUSAO'], errors='coerce')
    df['PREVISÃO CONCLUSÃO'] = pd.to_datetime(df['PREVISÃO CONCLUSÃO'], errors='coerce')
    df['PREVISAO_1A_INSP'] = pd.to_datetime(df['PREVISAO_1A_INSP'], errors='coerce')

    return df

df = carregar_dados()

# --- FILTROS ---
st.sidebar.header("Filtros")

# Filtro 1: Estratificação de Risco
risco = st.sidebar.selectbox("🔎 Estratificação de Risco", ["Todos", "Baixo Risco", "Médio Risco", "Alto Risco"])

# Filtro 2: Indicador
indicador = st.sidebar.selectbox("📌 Indicador", [
    "Inspeções realizadas em até 30 dias após a captação do processo",
    "Processos finalizados em até 90 dias após a captação do processo"
])

# Filtro 3: Período
data_min = df['ENTRADA'].min()
data_max = df['ENTRADA'].max()
periodo = st.sidebar.date_input("📆 Período", [data_min, data_max], min_value=data_min, max_value=data_max)

# --- APLICAR FILTROS ---
df_filtrado = df.copy()

# Filtrar por risco
if risco != "Todos":
    df_filtrado = df_filtrado[df_filtrado['CLASSIFICAÇÃO'].str.title() == risco]

# Filtrar por período
if len(periodo) == 2:
    df_filtrado = df_filtrado[(df_filtrado['ENTRADA'] >= periodo[0]) & (df_filtrado['ENTRADA'] <= periodo[1])]

# Adiciona colunas auxiliares
df_filtrado['ANO_MES'] = df_filtrado['ENTRADA'].dt.to_period("M").astype(str)

# --- AGRUPAMENTO ---
def calcula(grp):
    total = len(grp)
    if indicador == "Inspeções realizadas em até 30 dias após a captação do processo":
        validos = grp[grp['NUMERADOR_1'] == 1]
        num = len(validos)
    elif indicador == "Processos finalizados em até 90 dias após a captação do processo":
        grupo_valido = grp[
            ~grp['SITUAÇÃO'].isin(["EM INSPEÇÃO", "AGUARDANDO 1ª INSPEÇÃO", "PENDÊNCIA DOCUMENTAL"])
        ]
        grupo_valido = grupo_valido[grupo_valido['DATA_CONCLUSAO'] <= grupo_valido['PREVISÃO CONCLUSÃO']]
        num = len(grupo_valido)
    else:
        num = 0
    perc = (num / total) * 100 if total > 0 else 0
    return pd.Series({
        'Total Processos': total,
        'No Prazo': num,
        '% No Prazo': round(perc, 2)
    })

resultado = df_filtrado.groupby('ANO_MES').apply(calcula).reset_index()

# --- EXIBIR TABELA ---
st.subheader(f"📅 Desempenho Mensal: {indicador}")
st.dataframe(resultado)

# --- DOWNLOAD ---
def baixar_excel(df_resultado):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_resultado.to_excel(writer, index=False, sheet_name='Indicadores')
    return buffer.getvalue()

st.download_button(
    "📥 Baixar como Excel",
    data=baixar_excel(resultado),
    file_name="indicadores_visa_mes_a_mes.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Vigilância Sanitária de Ipojuca · 2025")
