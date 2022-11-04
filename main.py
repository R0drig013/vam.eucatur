import pandas as pd
import datetime
import statistics
import matplotlib.pyplot as plt
from PIL import Image
import requests
from bs4 import BeautifulSoup
import streamlit as st

icone = Image.open('icone.png')
st.set_page_config(
    page_title="VAM EUCATUR",
    page_icon=icone,
    layout="centered")

image = Image.open('logo.png')
st.image(image,width=250,)

st.title('VAM - Análise de Concorrência')


## FUNÇOES ## 
def limpa_str(info_pag):
    valo_limpo = ''
    for values in info_pag:
        if values.isdigit():
            valo_limpo = f'{valo_limpo}' + f'{values}'
    return valo_limpo

def limpa_str_valor(valor):
    valor_limpo = limpa_str(valor)
    qntd_dig = len(valor_limpo) - 2
    cont = 0
    valor_menor = ''
    valor_maior = ''
    for splitad in valor_limpo:
        cont += 1
        if cont <= qntd_dig:
            valor_menor = f'{valor_menor}' + splitad
        else:
            valor_maior = f'{valor_maior}' + splitad
    valor_final = f'{valor_menor}' + '.' + f'{valor_maior}'
    return valor_final

def limpa_str_horas(valor):
    valor_limpo = limpa_str(valor)
    qntd_dig = len(valor_limpo) - 2
    cont = 0
    valor_menor = ''
    valor_maior = ''
    for splitad in valor_limpo:
        cont += 1
        if cont <= qntd_dig:
            valor_menor = f'{valor_menor}' + splitad
        else:
            valor_maior = f'{valor_maior}' + splitad
    valor_final = f'{valor_menor}' + ':' + f'{valor_maior}'
    return valor_final

def rotas_concorrentes(saida, destino, ano, mes, dia):
    print(ano, mes, dia)
    print(f'DE {saida} PARA {destino}.')
    ender = requests.get(f'https://www.buscaonibus.com.br/horario/{saida}/{destino}?dt={dia}/{mes}/{ano}')
    ender_get = ender.content
    bea = BeautifulSoup(ender_get, 'html.parser')

    # HTML DA PAGINA
    feed = bea.findAll('div', attrs={'class': 'bo-timetable-info'})

    empresas = []
    lista_paramet = []
    lista_tempo = []

    cont = 0
    for info in feed:
        cont += 1

        preco = info.find('div', attrs={'class': 'bo-timetable-price'})
        empresa = info.find('div', attrs={'class': 'bo-timetable-company-name'})
        tipo_leito = info.find('div', attrs={'class': 'bo-timetable-type'})
        hr_saida = info.find('span', attrs={'class': 'bo-timetable-departure'})
        hr_chedada = info.find('span', attrs={'class': 'bo-timetable-arrival'})
        qtd_leito = info.find('div', attrs={'class': 'bo-timetable-seats'})

        preco_limpo = limpa_str_valor(preco.text)
        hr_saida_limpo = limpa_str_horas(hr_saida.text)
        hr_chedada_limpo = limpa_str_horas(hr_chedada.text)
        qtd_leito_limpo = limpa_str(qtd_leito.text)

        lista_tempo.append(datetime.date(int(ano),int(mes), int(dia)))
        lista_tempo.append(empresa.text)
        lista_tempo.append(preco_limpo)
        lista_tempo.append(hr_saida_limpo)
        lista_tempo.append(hr_chedada_limpo)
        lista_tempo.append(tipo_leito.text)
        lista_tempo.append(qtd_leito_limpo)

        if empresa.text == "Skyscanner":
            lista_tempo.append("Aviao")
        elif empresa.text == "BlaBlaCar":
            lista_tempo.append("Carro")
        else:
            lista_tempo.append("Onibus")

        lista_paramet = lista_tempo.copy()
        empresas.append(lista_paramet)
        lista_tempo.clear()

    return empresas

def plotarGrafComp(rota):
    d_precxdata = [float(x[2]) for x in rota if x[7] != "Aviao" and x[1] != "Eucatur"]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(d_precxdata)
    if len([float(x[2]) for x in rota if x[1] == "Eucatur"]) > 0:
        try:
            d_precxdataEucatur = [float(x[2]) for x in rota if x[1] == "Eucatur"]
            ax.violinplot(d_precxdataEucatur, widths=0.25)
            st.markdown("**Eucatur vs Concorrência**")
        except ValueError:  
            pass
    st.pyplot(fig)

def metricasConcorrencia(rota):
    col1, col2, col3 = st.columns(3)

    with col1:
        if len([float(x[2]) for x in rota if x[1] != "Eucatur"]) > 0:
            st.metric(label="Preço mínimo", value=str(round(min([float(x[2])for x in rota]),2)))
        if len([float(x[2]) for x in rota if x[1] == "Eucatur"]) > 0:
            st.metric(label="Preço mínimo Eucatur", value=str(round(min([float(x[2]) for x in rota if x[1] == "Eucatur"]), 2)),delta= str(round(min([float(x[2]) for x in rota if x[1] == "Eucatur"]) - min([float(x[2])for x in rota]) ,2)))

    with col2:
        if len([float(x[2]) for x in rota if x[1] != "Eucatur"]) > 0:
            st.metric(label="Preço médio", value=str(round(round(statistics.mean([float(x[2])for x in rota]),2),2)))
        if len([float(x[2]) for x in rota if x[1] == "Eucatur"]) > 0:
            st.metric(label="Preço médio Eucatur", value=str(round(statistics.mean([float(x[2]) for x in rota if x[1] == "Eucatur"]), 2)),delta= str(round(statistics.mean([float(x[2]) for x in rota if x[1] == "Eucatur"]) - statistics.mean([float(x[2])for x in rota]) ,2)))

    with col3:
        if len([float(x[2]) for x in rota if x[1] != "Eucatur"]) > 0:
            st.metric(label="Preço máximo", value=str(round(max([float(x[2])for x in rota]),2)))
        if len([float(x[2]) for x in rota if x[1] == "Eucatur"]) > 0:
            st.metric(label="Preço máximo Eucatur", value=str(round(max([float(x[2]) for x in rota if x[1] == "Eucatur"]), 2)),delta= str(round(max([float(x[2]) for x in rota if x[1] == "Eucatur"]) - max([float(x[2])for x in rota]) ,2)))

def TabelaDados(rota):
    df = pd.DataFrame(rota, columns=["Data", 'Empresa', "Preço", "Saída", "Chegada", "Tipo de Leito", "Assentos livres","Tipo"])
    st.dataframe(df, use_container_width=True)



col1, col2, col3 = st.columns(3)
with col1:
    origem = st.text_input("Origem")
with col2:
    destino = st.text_input("Destino")

with col3:
    date = st.date_input(
    "Data",  datetime.date.today())

if st.button('Buscar'):

    rotaRaiz = []
    lisDatas = []
    lisDatas1 = []
    for i in range(5):
        print(date)
        data1 = str(date)
        ano = data1[0:4]
        mes = data1[5:7]
        dia = data1[8:10]
        lisDatas.append(f"{dia}/{mes}/{ano}")
        lisDatas1.append(datetime.date(int(ano),int(mes),int(dia)))
        r1 = rotas_concorrentes(origem, destino, ano, mes, dia)
        date += datetime.timedelta(days=1)
        rotaRaiz += r1
    print(lisDatas)


    rota = rotaRaiz

    st.header(f"Dados de {lisDatas[0]} até {lisDatas[-1]}")

    metricasConcorrencia(rota)
    TabelaDados(rota)

    d_precxdata = [[float(y[2]) for y in rota if y[0] == x and y[7] != "Aviao" and y[1] != "Eucatur"] for x in lisDatas1]

    fig, ax = plt.subplots(figsize = (10,6))
    ax.boxplot(d_precxdata, labels = lisDatas)

    if len([float(x[2]) for x in rota if x[1] == "Eucatur"]) > 0:

        try:
            d_precxdataEucatur = [[float(y[2]) for y in rota if y[0] == x and y[1] == "Eucatur"] for x in lisDatas1]
            print(d_precxdataEucatur)
            ax.violinplot(d_precxdataEucatur,widths = 0.25)
            st.markdown("**Eucatur vs Concorrência**")            
        except ValueError:  
            pass

    st.pyplot(fig)

    st.header("Dados por dia ")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(lisDatas)

    with tab1:
        rota1 = [x for x in rotaRaiz if x[0] == lisDatas1[0]]
        st.header(lisDatas[0])

        metricasConcorrencia(rota1)
        TabelaDados(rota1)
        plotarGrafComp(rota1)


    with tab2:
        rota2 = [x for x in rotaRaiz if x[0] == lisDatas1[1]]
        st.header(lisDatas[1])

        metricasConcorrencia(rota2)
        TabelaDados(rota2)
        plotarGrafComp(rota2)

    with tab3:
        rota3 = [x for x in rotaRaiz if x[0] == lisDatas1[2]]
        st.header(lisDatas[2])
        
        metricasConcorrencia(rota3)
        TabelaDados(rota3)
        plotarGrafComp(rota3)

    with tab4:
        rota4 = [x for x in rotaRaiz if x[0] == lisDatas1[3]]
        st.header(lisDatas[3])

        metricasConcorrencia(rota4)
        TabelaDados(rota4)
        plotarGrafComp(rota4)

    with tab5:
        rota5 = [x for x in rotaRaiz if x[0] == lisDatas1[4]]
        st.header(lisDatas[4])

        metricasConcorrencia(rota5)
        TabelaDados(rota5)
        plotarGrafComp(rota5)

col1, col2, col3 = st.columns(3)

with col2:
    image3 = Image.open('AdN.png')
    st.image(image3,width=200,)
    st.caption("Developed by Gabriel e Rodrigo")