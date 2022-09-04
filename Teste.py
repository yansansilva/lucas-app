import streamlit as st
import pandas as pd
import re

#arquivo = r'C:\Users\yan_d\Desktop\Lucas_Dados\1 de maio 50cv 2'
arquivo1 = st.file_uploader("Upload Arquivo1")#, accept_multiple_files=True)

data = ''
tamanho = 1
lista = []

if arquivo1 is not None:
    info_Data = pd.read_csv(arquivo1, encoding='ISO-8859-1', header=None)
    if len(info_Data) != 1:
        arquivo2 = st.file_uploader("Upload Arquivo2")  # , accept_multiple_files=True)
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
        arquivo2 = st.file_uploader("Upload Arquivo2")  # , accept_multiple_files=True)
        arquivo3 = st.file_uploader("Upload Arquivo3")  # , accept_multiple_files=True)
        if arquivo2 is not None and arquivo3 is not None:
            info_Data2 = pd.read_csv(arquivo2, delimiter='\u0000', encoding='ISO-8859-1', header=None)[144].tolist()[0].split(',')[0]
            data = info_Data2[-8:]
            dados = pd.read_csv(arquivo3, delimiter=data, encoding='ISO-8859-1', header=None).iloc[:, 2:].replace(to_replace=',', value=f'{data},', regex=True).transpose().reset_index(drop=True).squeeze()
            lista = [re.sub('\u0000', ' ', x.lstrip()) for x in dados]

    if lista != []:
        separacao_lista = [[lista[x][0:17], lista[x][17:30], lista[x][30:43], lista[x][43:54], lista[x][54:65], lista[x][65:79]] for x in range(len(lista))]
        resultado = pd.DataFrame(separacao_lista, columns=['data', 'flow', 'velocidade', 'net', 'positive', 'negative'])
        st.write(resultado)
####-------------------------------------------------------------------------