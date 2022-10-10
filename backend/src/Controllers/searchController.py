from flask import Blueprint,request
from unidecode import unidecode
import pandas as pd
import numpy as np
import requests
import difflib
import random
import string 
import xlrd
import json
import os

diretorio = os.getcwd()

API_KEY = "c1d6039b74a493383fd998725a89b7ac2a331ebc23d4aaeba94700b0b8dc0c1a"

searchBP = Blueprint('search',__name__)

@searchBP.route("/search",methods = ["POST"])
def searcEngine():

    searchCity = request.get_json(force=True)

    try:
        searchCity["UF"]
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400
    

    searchCity["cidade"] = searchCity["cidade"].strip()
    
    if searchCity["UF"] == "":
        return json.dumps({"error":"Selecione um estado"}),400
    
    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400
    
    municipiosDF = pd.read_excel(diretorio+"/Dataset/Municipios.xlsx")
    
    UFDataset = municipiosDF.query("UF == '"+searchCity["UF"]+"'").reset_index(drop = True)

    if UFDataset.shape[0] == 0:
        return json.dumps({"error":"Municipio não encontrado"}),404

    cityUser = searchCity["cidade"]

    differenceArray = []
    for cityDF in UFDataset["Nome do Municipio"]:
        #Normalização das strings
        cityUser = cityUser.lower()
        cityDF = cityDF.lower()

        cityUser = unidecode(cityUser)
        cityUser = cityUser.translate(str.maketrans('', '',string.punctuation))

        cityDF = unidecode(cityDF)
        cityDF = cityDF.translate(str.maketrans('', '',string.punctuation))
        
        sequence = difflib.SequenceMatcher(isjunk= None, a = cityUser, b = cityDF)
        difference = sequence.ratio()
        difference = round(difference,2)
        differenceArray.append(difference)
    
    differenceArray = np.asarray(differenceArray)

    response = UFDataset["Nome do Municipio"][differenceArray.argmax()]
    
    line = 0
    CodMunic = 0
    for i in UFDataset["Nome do Municipio"]:
        if i == response:
            CodMunic = UFDataset["Cod.Munic"][line]
        line = line+1
    
    return json.dumps({"UF":searchCity["UF"],"Cod_Municipio":int(CodMunic),"Municipio":response})

@searchBP.route("/events",methods = ["POST"])            
def events():

    searchCity = request.get_json(force = True)
    
    try:
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400

    searchCity["cidade"] = searchCity["cidade"].strip()

    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400

    try:
        response = requests.get("https://serpapi.com/search.json?engine=google&q=Evento+em+"+searchCity["cidade"]+"&location=Brazil&google_domain=google.com.br&gl=br&hl=pt&api_key="+API_KEY)
        results = response.json()

        jsonReturn = {"Eventos": results["events_results"],"Mais_Eventos":results["more_events_link"]}
    except:
        return json.dumps({"error":"O lugar pesquisado não tem eventos disponiveis"}),404
    
    return json.dumps(jsonReturn),200

@searchBP.route("/places",methods = ["GET"])
def places():
    searchCity = request.get_json(force = True)
    searchLocal = request.get_json(force = True)

    try:
        searchCity["cidade"]
        searchLocal["searchLocal"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400

    searchCity["cidade"] = searchCity["cidade"].strip()
    searchCity["searchLocal"] = searchCity["searchLocal"].strip()

    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400
    
    if searchCity["searchLocal"] == "":
        return json.dumps({"error":"Digite algum local que deseja vistar (Ex: Restaurantes, Praças ou Museus)"}),400

    response = requests.get(f"https://serpapi.com/search.json?engine=google_maps&q="+searchLocal["searchLocal"]+" em "+searchCity["cidade"]+"&google_domain=google.com&hl=pt&type=search&api_key="+API_KEY)
    results = response.json()

    if results.get("error") != None:
        return json.dumps({"error":"Não foi encontrado nenhum "+searchLocal["searchLocal"]+" em "+searchCity["cidade"]}),404
    
    return json.dumps({"lugares":results["local_results"]}),200
    
@searchBP.route("/population",methods = ["POST"])
def population():
    searchCity = request.get_json(force=True)

    try:
        searchCity["UF"]
        searchCity["Cod_Municipio"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400
    
    searchCity["UF"] = searchCity["UF"].strip()
    searchCity["Cod_Municipio"] = searchCity["Cod_Municipio"].strip()

    if searchCity["Cod_Municipio"] == "":
        return json.dumps({"error":"Digite o código de um município"}),400
    
    if searchCity["UF"] == "":
        return json.dumps({"error":"Digie uma UF"}),400

    populationDF = pd.read_csv(diretorio+"/Dataset/População.csv", sep = ",")

    UFDataset = populationDF.query("UF == '"+searchCity["UF"]+"'").reset_index(drop = True)

    if UFDataset.shape[0] == 0:
        return json.dumps({"error":"Estado não encontrado"}),404
    
    line = 0
    searchBool = False

    Cod_Muni = int(searchCity["Cod_Municipio"])

    for i in UFDataset["COD. MUNIC"]:
        if i == Cod_Muni:
            searchBool = True
            population = UFDataset["POPULAÇÃO ESTIMADA"][line]
            return json.dumps({"success": population}),200
        line = line+1
    
    if searchBool == False:
        return json.dumps({"error":"A cidade digitada não foi encontrada"}),404

@searchBP.route("/city-image",methods = ["POST"])
def imagesCity():
    searchCity = request.get_json(force=True)

    try:
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400

    searchCity["cidade"] = searchCity["cidade"].strip()

    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400
    
    search = searchCity["cidade"]

    imageLink = requests.get(f"https://serpapi.com/search.json?engine=google&q=Imagem+de+"+search+"&location=Brazil&google_domain=google.com.br&gl=br&hl=pt&api_key="+API_KEY)

    imageResponse = imageLink.json()

    if imageResponse.get("error") != None:
        return json.dumps({"error":"Não foi encontrada nenhuma imagem"}),404

    image = imageResponse["inline_images"]
        
    randomImage = random.randrange(0,len(image))

    sendImage = image[randomImage]["original"]

    return json.dumps({"success":sendImage}),200


@searchBP.route("/weather", methods = ["POST"])
def weather():
    searchCity = request.get_json(force=True)

    try:
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400

    searchCity["cidade"] = searchCity["cidade"].strip()

    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400
    

    try:
        weather = requests.get("https://serpapi.com/search.json?engine=google&q=Tempo+"+searchCity["cidade"]+"&location=Brazil&google_domain=google.com&gl=br&hl=pt-br&device=desktop&api_key=c1d6039b74a493383fd998725a89b7ac2a331ebc23d4aaeba94700b0b8dc0c1a")
        weatherResponse = weather.json()

        weatherReturn = {"forecast":weatherResponse["answer_box"]["forecast"],"date":weatherResponse["answer_box"]["date"],"humidity":weatherResponse["answer_box"]["humidity"],"location":weatherResponse["answer_box"]["location"],"temperature":weatherResponse["answer_box"]["temperature"],"thumbnail":weatherResponse["answer_box"]["thumbnail"],"type":weatherResponse["answer_box"]["type"],"unit":weatherResponse["answer_box"]["unit"],"weather":weatherResponse["answer_box"]["weather"],"wind":weatherResponse["answer_box"]["wind"]}
    
        return weatherReturn,200
    except:
        return json.dumps({"error":"O clima dessa cidade não foi encontrado"})

@searchBP.route("/safety",methods = ["POST"])
def safety():
    city = request.get_json(force=True)
    try:
        city["cod_mun"]
        city["UF"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400

    city["cod_mun"] = city["cod_mun"].strip()
    city["UF"] = city["UF"].strip()

    if city["cod_mun"] == "":
        return json.dumps({"error":"Digite o código de um município"}),400
    
    if city["UF"] == "":
        return json.dumps({"error":"Digite o UF"}),400
    

    def tratar_dados_pop_ibge_est(diretorio):
        caminho = (r'' + diretorio + '\Dataset\Populacao.xls')
        dados_pop = xlrd.open_workbook(caminho)
        dados_pop.sheet_names()
        dataset_pop_mun = pd.read_excel(
            dados_pop, engine='xlrd', sheet_name=dados_pop.sheet_names()[1])
        dataset_pop_mun = dataset_pop_mun.dropna()
        dataset_pop_mun.columns = dataset_pop_mun.iloc[0]
        dataset_pop_mun = dataset_pop_mun.iloc[1:, ].reindex()
        dataset_pop_mun.dtypes
        dataset_pop_mun.isnull().sum()
        dataset_pop_mun.iloc[:, 0].value_counts()
        dataset_pop_mun_not_num = dataset_pop_mun[dataset_pop_mun["POPULAÇÃO ESTIMADA"].str.contains(
            '()', na=False)]
        dataset_pop_mun_not_num
        dataset_pop_mun_not_num["POPULAÇÃO ESTIMADA"] = dataset_pop_mun_not_num["POPULAÇÃO ESTIMADA"].str.replace(
            r"\(.*\)", '', regex=True)
        dataset_pop_mun.loc[dataset_pop_mun["POPULAÇÃO ESTIMADA"].str.contains('()', na=False)] = dataset_pop_mun.loc[dataset_pop_mun["POPULAÇÃO ESTIMADA"].str.contains('()', na=False)]\
            .astype(str).replace(r"\(.*\)", '', regex=True)
        dataset_pop_mun["POPULAÇÃO ESTIMADA"] = pd.to_numeric(
            dataset_pop_mun["POPULAÇÃO ESTIMADA"])
        dataset_pop_mun["COD. MUNIC"] = dataset_pop_mun["COD. MUNIC"].str.extract(r'(\d{,4})')
        dataset_pop_mun["COD. MUNIC"] = dataset_pop_mun["COD. UF"].astype(str) + dataset_pop_mun["COD. MUNIC"].astype(str)
        return dataset_pop_mun
    dataset_pop_tratado = tratar_dados_pop_ibge_est(diretorio=diretorio)

    def tratar_dados_mortalidade(diretorio, dataset_pop):
        dataset_mort =  pd.read_csv(diretorio + '\Dataset\Mortalidade.csv', sep = ";", encoding='iso-8859-1', skiprows= 4, nrows=3739)
        dataset_mort['Código Município'] = dataset_mort.Município.str.split("(\d+)", expand= True)[1]
        dataset_mort['Município'] = dataset_mort.Município.str.replace(r'(\d+)', '', regex= True)
        dataset_mort['Código UF'] = dataset_mort['Código Município'].str[:2]
        dataset_mort = dataset_mort.merge(dataset_pop[["COD. MUNIC", "POPULAÇÃO ESTIMADA", "UF"]], how = 'left', left_on = ["Código Município"], right_on = ["COD. MUNIC"]).drop(["COD. MUNIC"], axis = 1)
        dataset_mort['Mortalidade por 100 mil habitantes'] = ((dataset_mort["Óbitos_p/Ocorrênc"]/dataset_mort["POPULAÇÃO ESTIMADA"]) * 100000).round(decimals = 1)
        dataset_mort = dataset_mort.sort_values("Mortalidade por 100 mil habitantes").reset_index()
        return dataset_mort

    def media_mortalidade(dataset, estado):
        media_estado = dataset.loc[dataset['UF']==estado]["Mortalidade por 100 mil habitantes"].mean()
        return round(media_estado, 1)
    def ranking_nacional(dataset, cod):
        ranking_nacional = ((dataset.index[dataset['Código Município']== cod][0]).astype('int64') + 1)
        return ranking_nacional 
    def ranking_estadual(dataset, cod,uf):
        dataset_est = (dataset.loc[dataset['UF']==uf]).reset_index()
        ranking_estadual = ((dataset_est.index[dataset_est['Código Município']== cod][0]).astype('int64') + 1)
        return ranking_estadual
    def situacao_mortalidade(dataset, cod, uf):
        media_est = media_mortalidade(dataset, uf)
        posicao = ranking_nacional(dataset, cod)
        mort_municipio = dataset["Mortalidade por 100 mil habitantes"].values[posicao - 1]
        if mort_municipio < media_est:
            return "A taxa de mortalidade do municipio é menor que a média do estado"
        else: 
            return "A taxa de mortalidade do municipio é maior que a média do estado"

    dataset_mort_tratado = tratar_dados_mortalidade(diretorio,dataset_pop_tratado)

    def found_mun(cod_mun,uf):
        line = 0
        achou = False
        for i in dataset_mort_tratado["Código Município"]:
            if i == cod_mun:
                if dataset_mort_tratado["UF"][line] == uf:
                    achou = True
                    return True
            line = line+1
        
        return achou
    
    if found_mun(cod_mun= city["cod_mun"],uf = city["UF"]) == False:
        return json.dumps({"error":"Métricas de segurança do município não encontradas"}),404
    
    ranking_nacional__mun = ranking_nacional(dataset_mort_tratado, city["cod_mun"])
    ranking_estadual__mun = ranking_estadual(dataset_mort_tratado, city["cod_mun"], city["UF"])
    situacao = situacao_mortalidade(dataset_mort_tratado, city["cod_mun"], city["UF"])

    response = json.dumps({"ranking_mortalidade_nacional":str(ranking_nacional__mun),"ranking_mortalidade_estadual":str(ranking_estadual__mun),"média":str(situacao)})
    return response,200


