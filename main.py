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

observacao = st.checkbox('Mostrar Observações')
if observacao:
    st.write('''**_Será necessário abrir o mesmo arquivo duas ou três vezes:_** \n
    - 2 vezes, se o arquivo estiver bugado. \n
    - 3 vezes, se o arquivo estiver normal. \n
    - Quando for feito o upload do arquivo, serão solitadas automaticamente a quantidade de vezes necessária para executar o programa \n
    - Ao término da execução do programa, será possível ver o resultado na própria página da web, além de fazer o download do resultado
    no formato Excel ou CSV.''')

coluna_1, coluna_2, coluna_3 = st.columns((3, 3, 3))
arquivo1 = coluna_1.file_uploader("Primeiro Upload do Arquivo")#, accept_multiple_files=True)

data = ''
tamanho = 1
lista = []
resultado = pd.DataFrame()

if arquivo1 is not None:
    info_Data = pd.read_csv(arquivo1, encoding='ISO-8859-1', header=None)
    if len(info_Data) != 1:
        arquivo2 = coluna_2.file_uploader("Segundo Upload do Arquivo")  # , accept_multiple_files=True)
        data = info_Data[0][1]
        if arquivo2 is not None:
            dados = pd.read_csv(arquivo2, delimiter=data, encoding='ISO-8859-1', header=None).iloc[:, 1:].replace(to_replace=',', value=f'{data},', regex=True).transpose().reset_index(drop=True)
            organizar_dados = pd.DataFrame()
            for x in range(len(dados.columns)):
                df_auxiliar = pd.DataFrame(dados[x])
                df_auxiliar.columns = ['0']
                organizar_dados = pd.concat([organizar_dados, df_auxiliar], ignore_index=True).dropna().reset_index(drop=True)
            dados_organizados = organizar_dados.squeeze()
            lista = [re.sub('\u0000', ' ', x.lstrip()) for x in dados_organizados]
    else:
        arquivo2 = coluna_2.file_uploader("Segundo Upload do Arquivo")  # , accept_multiple_files=True)
        arquivo3 = coluna_3.file_uploader("Terceiro Upload do Arquivo")  # , accept_multiple_files=True)
        if arquivo2 is not None and arquivo3 is not None:
            info_Data2 = pd.read_csv(arquivo2, delimiter='\u0000', encoding='ISO-8859-1', header=None)[144].tolist()[0].split(',')[0]
            data = info_Data2[-8:]
            dados = pd.read_csv(arquivo3, delimiter=data, encoding='ISO-8859-1', header=None).iloc[:, 2:].replace(to_replace=',', value=f'{data},', regex=True).transpose().reset_index(drop=True).squeeze()
            lista = [re.sub('\u0000', ' ', x.lstrip()) for x in dados]

    if lista != []:
        separacao_lista = [[lista[x][0:17], float(lista[x][17:30]), float(lista[x][30:43]), float(lista[x][43:54]), float(lista[x][54:65]), float(lista[x][65:79])] for x in range(len(lista))]
        resultado = pd.DataFrame(separacao_lista, columns=['data', 'flow', 'velocidade', 'net', 'positive', 'negative'])
        mostrar = st.checkbox('Exibir Resultados')
        if mostrar:
            st.dataframe(resultado)

if not resultado.empty:
	st.write("### Salvar Resultados")

	coluna_nomear_arquivo_1, coluna_nomear_arquivo_2 = st.columns((3, 2))
	nomearquivo = coluna_nomear_arquivo_1.text_input('Digite um nome para o arquivo:', f'arquivo-{data}_convertido')

	coluna_salvar_1, coluna_salvar_2, coluna_salvar_3 = st.columns((2, 2, 6))
	csv = converter_df_csv(resultado)
	excel = converter_df_excel(resultado)
	coluna_salvar_1.download_button(label="Download em CSV", data=csv, file_name=nomearquivo + '.csv', mime='text/csv')
	coluna_salvar_2.download_button(label="Download em Excel", data=excel, file_name=nomearquivo+'.xlsx', mime='application/vnd.ms-excel')
