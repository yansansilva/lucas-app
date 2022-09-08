import streamlit as st
import pandas as pd
import re
from io import BytesIO
import xlsxwriter
import openpyxl

st.set_page_config(
	layout="wide"
)

@st.cache
def converter_df_csv(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

@st.cache
def converter_df_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Plan1')
    workbook = writer.book
    worksheet = writer.sheets['Plan1']
    format1 = workbook.add_format({'num_format': '0.00'})
    worksheet.set_column('A:A', None, format1)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

coluna_1, coluna_2, coluna_3 = st.columns((3, 3, 3))
arquivo = coluna_1.file_uploader("Upload do Arquivo")#, accept_multiple_files=True)

lista = []
resultado = pd.DataFrame()

if arquivo is not None:
    espaco='\u0000'
    dados_importados = pd.read_csv(arquivo, delimiter=f'No Liner{11*espaco}0.  Water{19*espaco}', encoding='ISO-8859-1', header=None)
    if len(dados_importados) != 1:
        dados_concatenados = pd.concat([dados_importados[1], dados_importados[0]], ignore_index=True).dropna().reset_index(drop=True).drop(labels=1).reset_index(drop=True).squeeze()#[0].split(',')
        dados_em_lista = []
        for x in range(len(dados_concatenados)):
            dados_em_lista.append(dados_concatenados[x].split(','))
        dados_transpostos = pd.DataFrame(dados_em_lista).transpose()
        dados_concatenados_2 = pd.DataFrame()
        for x in range(len(dados_transpostos.columns)):
            dados_concatenados_2 = pd.concat([dados_concatenados_2, pd.DataFrame(dados_transpostos)[x]], ignore_index=True)
        dados = dados_concatenados_2.dropna().reset_index(drop=True).squeeze().tolist()
    else:
        dados = dados_importados.squeeze()[1].split(',')


    lista_dados = []
    for linha, dado in enumerate(dados):
        if len(dado) > 10:
            if 0 < linha < len(dados) - 1:
                if len(dados[linha + 1]) <= 10:
                    lista_dados.append([f'{dados[linha - 1][-8:]},{dado[:-1]}'])
                else:
                    lista_dados.append([f'{dados[linha - 1][-8:]},{dado[:-9]}'])
            else:
                lista_dados.append([f'{dados[linha - 1][-8:]},{dado[:-1]}'])

    lista = [re.sub('\u0000', ' ', x.lstrip()) for x in pd.DataFrame(lista_dados).squeeze()]

    if lista != []:
        separacao_lista = [[lista[x][0:17], float(lista[x][17:30]), float(lista[x][30:43]), float(lista[x][43:54]), float(lista[x][54:65]), float(lista[x][65:79])] for x in range(len(lista))]
        resultado = pd.DataFrame(separacao_lista, columns=['data', 'flow', 'velocidade', 'net', 'positive', 'negative'])
        mostrar = st.checkbox('Exibir Resultados')
        if mostrar:
            st.dataframe(resultado)

if not resultado.empty:
    data = [resultado['data'][resultado.index[0]][:8], resultado['data'][resultado.index[-1]][:8]]

    st.write("### Salvar Resultados")

    coluna_nomear_arquivo_1, coluna_nomear_arquivo_2 = st.columns((3, 2))
    if data[0] != data[1]:
        nomearquivo = coluna_nomear_arquivo_1.text_input('Digite um nome para o arquivo:', f'medição_de_{data[0]}_a_{data[1]}')
    else:
        nomearquivo = coluna_nomear_arquivo_1.text_input('Digite um nome para o arquivo:', f'medição_de_{data[0]}')

    coluna_salvar_1, coluna_salvar_2, coluna_salvar_3 = st.columns((2, 2, 6))
    csv = converter_df_csv(resultado)
    excel = converter_df_excel(resultado)
    coluna_salvar_1.download_button(label="Download em CSV", data=csv, file_name=nomearquivo + '.csv', mime='text/csv')
    coluna_salvar_2.download_button(label="Download em Excel", data=excel, file_name=nomearquivo+'.xlsx', mime='application/vnd.ms-excel')
