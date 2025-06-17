import streamlit as st
import pandas as pd
import io

# URL da planilha Google Sheets (aba 'GERAL')
SHEET_ID = '1MpjevwLmc4w0OF4ffZEaOhd5hLWaH6FL'
GID = '793227745'
CSV_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}'

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
    st.set_page_config(page_title='Painel Gratificação SUS', layout='wide')
    st.title('Painel de Indicadores - Gratificação SUS')

    df = load_data()
    st.sidebar.header('Filtros')

    # Ajuste dos nomes das colunas conforme a planilha
    col_mes = 'Mês'
    col_indicador = 'Indicador'
    col_valor = 'Valor'
    col_meta = 'Meta'

    # Filtros na barra lateral
    meses = df[col_mes].dropna().unique().tolist()
    meses.sort()
    indicadores = df[col_indicador].dropna().unique().tolist()
    indicadores.sort()

    mes_selecionado = st.sidebar.multiselect('Selecione o(s) Mês(es):', meses, default=meses)
    indicador_selecionado = st.sidebar.multiselect('Selecione o(s) Indicador(es):', indicadores, default=indicadores)

    # Filtragem dos dados
    df_filtrado = df[(df[col_mes].isin(mes_selecionado)) & (df[col_indicador].isin(indicador_selecionado))]

    st.subheader('Resumo da Seleção')

    for indicador in indicador_selecionado:
        st.markdown(f'### Indicador: {indicador}')
        df_indicador = df_filtrado[df_filtrado[col_indicador] == indicador]

        st.dataframe(df_indicador)

        if not df_indicador.empty:
            try:
                valor_medio = df_indicador[col_valor].astype(float).mean()
                meta = df_indicador[col_meta].astype(float).iloc[0]

                if indicador == 'Indicador 3':
                    st.info(f"Apresentação individual dos dados do Indicador 3.")
                else:
                    st.metric(label='Média do Indicador', value=round(valor_medio, 2))

                if valor_medio >= meta:
                    st.success(f'Meta alcançada! (Meta: {meta})')
                else:
                    st.error(f'Meta não alcançada. (Meta: {meta})')

            except Exception as e:
                st.warning('Não foi possível calcular a média ou meta devido a dados não numéricos.')

    # Botão de download dos dados filtrados
    if not df_filtrado.empty:
        excel_data = to_excel(df_filtrado)
        st.download_button(
            label='📥 Baixar dados filtrados (.xlsx)',
            data=excel_data,
            file_name='dados_gratificacao_sus.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.warning('Nenhum dado disponível para os filtros selecionados.')

if __name__ == '__main__':
    main()
