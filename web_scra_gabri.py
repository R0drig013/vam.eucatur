import datetime
import requests
from bs4 import BeautifulSoup
import json


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

        # lista_tempo.append(datetime.date(int(ano),int(mes), int(dia)))
        lista_tempo.append(str(datetime.date(int(ano), int(mes), int(dia))))
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

        lista_tempo.append(saida)
        lista_tempo.append(destino)
        lista_tempo.append(saida + " - " + destino)
        # lista_tempo.append(datetime.date.today())
        lista_tempo.append(str(datetime.date.today()))

        lista_paramet = lista_tempo.copy()
        empresas.append(lista_paramet)
        lista_tempo.clear()

    return empresas


Lorigem = ["São Paulo", "Curitiba", "Florianópolis", 'Cuiabá', "Campo grande", "Cuiabá", "Cascavel", 'Cascavel']

Ldestino = ["Curitiba", "Porto Alegre", "São Paulo", "Vilhena", "Maringá", "Campo Grande", "Campo Grande",
            "Porto Alegre"]

dados = {}

for i in range(len(Lorigem)):
    origem = Lorigem[i]
    destino = Ldestino[i]
    print(f"{Lorigem[i]} - {Ldestino[i]}")
    date = datetime.date.today()

    rotaRaiz = []
    for j in range(7):
        print(date)
        data1 = str(date)
        ano = data1[0:4]
        mes = data1[5:7]
        dia = data1[8:10]
        r1 = rotas_concorrentes(origem, destino, ano, mes, dia)
        date += datetime.timedelta(days=1)
        rotaRaiz += r1
    print(rotaRaiz)
    dados[f"{Lorigem[i]} - {Ldestino[i]}"] = rotaRaiz

with open("dadosConcorrencia.json", "w") as json_file:
    json.dump(dados, json_file, indent=4)