import streamlit as st
import pandas as pd
import io

# URL para exportar a aba da planilha google como csv
# (Pega o ID da planilha e gid da aba)
SHEET_ID = "19Vvz80VUZgHBaiFq1YTxOXJHBFl_EkfX"
GID = "1287749088"

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados Filtrados')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

def main():
    st.title("Painel Gratificação SUS")

    df = load_data()

    # Assumindo que existe uma coluna 'Mês' e 'Pasta de trabalho' que indicam os filtros
    meses = df['Mês'].dropna().unique()
    meses = sorted(meses, key=lambda x: str(x))  # Ordena alfabeticamente (ou ajustar ordem de meses se desejar)

    indicadores = df['Pasta de trabalho'].dropna().unique()
    indicadores = sorted(indicadores)

    # Sidebar filtros
    st.sidebar.header("Filtros")

    mes_selecionado = st.sidebar.multiselect("Selecione o(s) mês(es):", meses, default=meses)
    indicador_selecionado = st.sidebar.multiselect("Selecione o(s) indicador(es):", indicadores, default=indicadores)

    # Filtra dataframe
    df_filtrado = df[
        (df['Mês'].isin(mes_selecionado)) &
        (df['Pasta de trabalho'].isin(indicador_selecionado))
    ]

    st.subheader("Resumo da Seleção")
    st.dataframe(df_filtrado)

    # Botão para download Excel
    if not df_filtrado.empty:
        excel_data = to_excel(df_filtrado)
        st.download_button(
            label="Baixar dados filtrados (.xlsx)",
            data=excel_data,
            file_name='dados_gratificacao_sus.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

if __name__ == "__main__":
    main()
