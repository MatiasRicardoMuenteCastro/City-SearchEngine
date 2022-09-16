#from sklearn.feature_extraction.text import CountVectorizer
from flask import Blueprint,request
from unidecode import unidecode
import string 
import difflib
import pandas as pd
import requests
import json

API_KEY = "9b6a3807991240c07ccb2d1c93d0b23ee6d4b33c8c2cb32fc2e79e707f982572"

searchBP = Blueprint('search',__name__)

@searchBP.route("/search",methods = ["GET"])
def searcEngine():

    searchCity = request.get_json(force=True)

    try:
        searchCity["UF"]
        searchCity["cidade"]
    except:
        return json.dumps({"error":"JSON mal formatado"}),400

    municipiosDF = pd.read_excel("./backend/src/Dataset/Municipios.xlsx")
    
    searchCity["cidade"] = searchCity["cidade"].strip()
    
    if searchCity["UF"] == "":
        return json.dumps({"error":"Selecione um estado"}),400
    
    if searchCity["cidade"] == "":
        return json.dumps({"error":"Digite o nome de um município"}),400

    UFDataset = municipiosDF.query("UF == '"+searchCity["UF"]+"'")
    print(UFDataset)

    cityUser = "São Paulo"
    cityDF = "São Paulo"

    #Normalização das strings
    cityUser = cityUser.lower()
    cityDF = cityDF.lower()

    cityUser = unidecode(cityUser)
    cityUser = cityUser.translate(str.maketrans('', '',string.punctuation))

    cityDF = unidecode(cityDF)
    cityDF = cityDF.translate(str.maketrans('', '',string.punctuation))
    
    print(cityUser, cityDF)

    sequence = difflib.SequenceMatcher(isjunk= None, a = cityUser, b = cityDF)
    difference = sequence.ratio()
    difference = round(difference,2)
    print(difference) 

    """
    n = 1

    separator = CountVectorizer(analyzer = "word",ngram_range = (n,n))

    separadorInt = separator.fit([cidadeUser,cidadeDF]).vocabulary_

    counts = CountVectorizer(analyzer="word",ngram_range=(n,n))
    
    n_grams = counts.fit_transform([cidadeUser,cidadeDF])
    
    vocab2int = counts.fit([cidadeUser,cidadeDF]).vocabulary_

    n_grams_array = n_grams.toarray()

    print("Vetor de n-gramas:\n\n",n_grams_array)
    print()
    print("Dicionario de n-gramas:",vocab2int)

    n_grams.toarray()

    intersection_list = np.amin(n_grams.toarray(), axis = 0)

    intersection_count = np.sum(intersection_list)

    index_A = 0

    A_count = np.sum(n_grams.toarray()[index_A])
    
    print(intersection_count/A_count)
    """
    return json.dumps({"error":"a"})

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
        return json.dumps({"Error":"O lugar pesquisado não tem eventos disponiveis"}),404
    
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


    try:
        response = requests.get(f"https://serpapi.com/search.json?engine=google_maps&q="+searchLocal["searchLocal"]+" em "+searchCity["cidade"]+"&google_domain=google.com&hl=pt&type=search&api_key="+API_KEY)
        results = response.json()

        return json.dumps({"Lugares":results["local_results"]}),200
    except:
        return json.dumps({"error":"Municipio pesquisado, ou o lugar que você pesquisou não encontrado"}),400
    



@searchBP.route("/weather", methods = ["GET"])
def weather():
    return json.dumps({"Success":"Clima legal"}),200

@searchBP.route("/population",methods = ["GET"])
def population():
    return json.dumps({"Success":"População maneira"}),200