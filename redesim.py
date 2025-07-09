import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

# ---🔐 LOGIN SIMPLES ---
def login():
    st.title("🔐 Painel de Indicadores da Vigilância Sanitária de Ipojuca")
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

# ========== CONFIGURAÇÃO ==========
st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("📊 Indicadores por Mês - VISA Ipojuca")

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

    df['MÊS'] = df['ENTRADA'].dt.month
    df['ANO'] = df['ENTRADA'].dt.year

    return df

df = carregar_dados()

# ========== FILTROS ==========
st.sidebar.header('Filtros')

risco = st.sidebar.multiselect("Estratificação de Risco", ["Baixo Risco", "Médio Risco", "Alto Risco"])

indicador = st.sidebar.selectbox(
    "Indicador",
    ["Inspeções realizadas em até 30 dias após a captação do processo",
     "Processos finalizados em até 90 dias após a captação do processo"]
)

anos_disponiveis = sorted(df['ANO'].dropna().unique(), reverse=True)
ano = st.sidebar.selectbox("Ano", anos_disponiveis)

meses_nome = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

meses = st.sidebar.multiselect("Meses", options=list(meses_nome.keys()), format_func=lambda x: meses_nome[x])

# Aplicar filtros
filtro_df = df[(df['ANO'] == ano) & (df['MÊS'].isin(meses))]
if risco:
    filtro_df = filtro_df[filtro_df['CLASSIFICAÇÃO'].str.title().isin(risco)]

# ========== CÁLCULOS ==========
resultado = []

for mes in sorted(filtro_df['MÊS'].unique()):
    nome_mes = meses_nome[mes]
    df_mes = filtro_df[filtro_df['MÊS'] == mes]

    if indicador == "Inspeções realizadas em até 30 dias após a captação do processo":
        df_validos = df_mes[~df_mes['SITUAÇÃO'].isin(["AGUARDANDO 1ª INSPEÇÃO", "PENDÊNCIA DOCUMENTAL"])]
        df_numerador = df_validos[df_validos['1ª INSPEÇÃO'] <= df_validos['PREVISAO_1A_INSP']]
        num = len(df_numerador)
        den = len(df_validos)
    else:
        df_validos = df_mes[~df_mes['SITUAÇÃO'].isin(["EM INSPEÇÃO", "AGUARDANDO 1ª INSPEÇÃO", "PENDÊNCIA DOCUMENTAL"])]
        df_numerador = df_validos[df_validos['DATA_CONCLUSAO'] <= df_validos['PREVISÃO CONCLUSÃO']]
        num = len(df_numerador)
        den = len(df_validos)

    perc = (num / den * 100) if den > 0 else 0
    resultado.append({
        "Mês": nome_mes,
        "Numerador": num,
        "Denominador": den,
        "Percentual (%)": round(perc, 2)
    })

# ========== EXIBIÇÃO ==========
st.subheader(f"Resultado: {indicador}")

df_resultado = pd.DataFrame(resultado)
st.dataframe(df_resultado)

# ========== DOWNLOAD ==========
def gerar_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    return output.getvalue()

st.download_button(
    label="📥 Baixar dados usados no cálculo",
    data=gerar_excel(filtro_df),
    file_name="dados_filtrados_indicadores.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Vigilância Sanitária de Ipojuca - 2025")
