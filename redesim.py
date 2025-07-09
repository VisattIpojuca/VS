import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---🔐 LOGIN SIMPLES ---
def login():
    st.title("🔐 Painel de Monitoramento de Indicadores da Vigilância Sanitária de Ipojuca")
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

# ========== PAINEL ==========
st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

@st.cache_data
def carregar_dados():
    url = (
        "https://docs.google.com/spreadsheets/d/"
        "1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv&gid=502962216"
    )
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

# Filtros
st.sidebar.header('Filtros')
filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', sorted(df['PROTOCOLO'].dropna().unique()))
filtro_cnpj = st.sidebar.multiselect('CNPJ', sorted(df['CNPJ'].dropna().unique()))
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', sorted(df['ESTABELECIMENTO'].dropna().unique()))
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', sorted(df['ATIVIDADE'].dropna().unique()))
filtro_classificacao = st.sidebar.multiselect('CLASSIFICAÇÃO', sorted(df['CLASSIFICAÇÃO'].dropna().unique()))
filtro_territorio = st.sidebar.multiselect('TERRITÓRIO', sorted(df['TERRITÓRIO'].dropna().unique()))
filtro_situacao = st.sidebar.multiselect('SITUAÇÃO', sorted(df['SITUAÇÃO'].dropna().unique()))

# Período
data_min = df['ENTRADA'].min()
data_max = df['ENTRADA'].max()
data_inicio, data_fim = st.sidebar.date_input('PERÍODO', [data_min, data_max], min_value=data_min, max_value=data_max)

# Indicador
indicador_selecionado = st.sidebar.selectbox(
    "Selecione o Indicador",
    ["", "1ª Visita em até 30 dias", "Processo finalizado em até 90 dias"]
)

# Aplicar filtros
df_filtrado = df.copy()
if filtro_protocolo:
    df_filtrado = df_filtrado[df_filtrado['PROTOCOLO'].isin(filtro_protocolo)]
if filtro_cnpj:
    df_filtrado = df_filtrado[df_filtrado['CNPJ'].isin(filtro_cnpj)]
if filtro_estab:
    df_filtrado = df_filtrado[df_filtrado['ESTABELECIMENTO'].isin(filtro_estab)]
if filtro_atividade:
    df_filtrado = df_filtrado[df_filtrado['ATIVIDADE'].isin(filtro_atividade)]
if filtro_classificacao:
    df_filtrado = df_filtrado[df_filtrado['CLASSIFICAÇÃO'].isin(filtro_classificacao)]
if filtro_territorio:
    df_filtrado = df_filtrado[df_filtrado['TERRITÓRIO'].isin(filtro_territorio)]
if filtro_situacao:
    df_filtrado = df_filtrado[df_filtrado['SITUAÇÃO'].isin(filtro_situacao)]

df_filtrado = df_filtrado[
    (df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) &
    (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))
]

# Indicador 1: baseado na coluna Q ("NUMERADOR_1")
if indicador_selecionado == "1ª Visita em até 30 dias":
    df_validos = df_filtrado.copy()

    if 'NUMERADOR_1' in df_validos.columns:
        df_validos['NUMERADOR_1'] = pd.to_numeric(df_validos['NUMERADOR_1'], errors='coerce').fillna(0).astype(int)
        df_numerador = df_validos[df_validos['NUMERADOR_1'] == 1]
    else:
        st.warning("A coluna 'Numerador 1' (coluna Q) não foi encontrada.")
        df_numerador = pd.DataFrame([])

    numerador = len(df_numerador)
    denominador = len(df_validos)
    percentual = (numerador / denominador * 100) if denominador > 0 else 0

    st.markdown(f"""
    ## 🕒 Indicador: 1ª Visita em até 30 dias
    - ✅ **{percentual:.2f}%** no prazo
    - 🎯 **Numerador:** {numerador}
    - 📊 **Denominador:** {denominador}
    """)

elif indicador_selecionado == "Processo finalizado em até 90 dias":
    df_90 = df_filtrado[
        ~df_filtrado['SITUAÇÃO'].isin(["EM INSPEÇÃO", "AGUARDANDO 1ª INSPEÇÃO", "PENDÊNCIA DOCUMENTAL"])
    ]

    filtro_valido_90 = (
        df_90['DATA_CONCLUSAO'].notna() &
        (df_90['DATA_CONCLUSAO'] <= df_90['PREVISÃO CONCLUSÃO'])
    )

    numerador_90 = filtro_valido_90.sum()
    denominador_90 = len(df_filtrado)
    percentual_90 = (numerador_90 / denominador_90 * 100) if denominador_90 > 0 else 0

    st.markdown(f"""
    ## 📜 Indicador: Processo finalizado em até 90 dias
    - ✅ **{percentual_90:.2f}%** no prazo
    - 🎯 **Numerador:** {numerador_90}
    - 📊 **Denominador:** {denominador_90}
    """)

# Gráficos
st.subheader("Visualização dos Dados")

if not df_filtrado.empty:
    g1 = px.bar(df_filtrado, x='TERRITÓRIO', color='CLASSIFICAÇÃO', title='Inspeções por Território')
    st.plotly_chart(g1, use_container_width=True)

    g2 = px.histogram(df_filtrado, x='CLASSIFICAÇÃO', title='Distribuição por Classificação')
    st.plotly_chart(g2, use_container_width=True)

# Tabela com datas formatadas
st.subheader("Tabela de Dados Filtrados")
for col in ['ENTRADA', '1ª INSPEÇÃO', 'DATA_CONCLUSAO', 'PREVISÃO CONCLUSÃO', 'PREVISAO_1A_INSP']:
    if col in df_filtrado.columns:
        df_filtrado[col] = pd.to_datetime(df_filtrado[col], errors='coerce').dt.strftime('%d/%m/%Y')

st.dataframe(df_filtrado)
st.caption("Vigilância Sanitária de Ipojuca - 2025")