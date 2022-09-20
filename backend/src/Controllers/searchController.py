from flask import Blueprint,request
from unidecode import unidecode
import random
import pandas as pd
import numpy as np
import string 
import difflib
import requests
import json

API_KEY = "c1d6039b74a493383fd998725a89b7ac2a331ebc23d4aaeba94700b0b8dc0c1a"

searchBP = Blueprint('search',__name__)

@searchBP.route("/search",methods = ["GET"])
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
    
    municipiosDF = pd.read_excel("./backend/src/Dataset/Municipios.xlsx")
    
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

    return json.dumps({"UF":searchCity["UF"],"Success":response})

@searchBP.route("/events",methods = ["GET"])            
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
    
    return json.dumps({"Lugares":results["local_results"]}),200
    
@searchBP.route("/population",methods = ["GET"])
def population():
    searchCity = request.get_json(force=True)

    try:
        searchCity["UF"]
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400
    
    searchCity["UF"] = searchCity["UF"].strip()
    searchCity["cidade"] = searchCity["cidade"].strip()

    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400
    
    if searchCity["UF"] == "":
        return json.dumps({"error":"Digie uma UF"}),400

    populationDF = pd.read_excel("./backend/src/Dataset/População.xlsx")

    UFDataset = populationDF.query("UF == '"+searchCity["UF"]+"'").reset_index(drop = True)

    if UFDataset.shape[0] == 0:
        return json.dumps({"error":"Municipio não encontrado"}),404
    
    line = 0
    searchBool = False

    for i in UFDataset["NOME DO MUNICÍPIO"]:
        if i == searchCity["cidade"]:
            searchBool = True
            population = UFDataset["POPULAÇÃO ESTIMADA"][line]
            return json.dumps({"success": population}),200
        line = line+1
    
    if searchBool == False:
        return json.dumps({"error":"A cidade digitada não foi encontrada"}),404

@searchBP.route("/city-image",methods = ["GET"])
def imagesCity():
    searchCity = request.get_json(force=True)

    try:
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),40

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

    return json.dumps({"Success":sendImage}),200


@searchBP.route("/weather", methods = ["GET"])
def weather():
    return json.dumps({"Success":"Clima maneiro"}),200

@searchBP.route("/safety",methods = ["GET"])
def safety():
    return json.dumps({"Success":"Segurança maneira"}),200


