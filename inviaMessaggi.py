from util.ripartizione import main as ripartizione
import sys
import logging
import requests
import json
import util.statics as statics
from requests.exceptions import HTTPError

verbose = False
path = "logs/inviamessaggi.log"
maxResults = 10
statics.session = ""
statics.baseUrl = ""
apiUsername = ""
apiPassword = ""

#Lettura file di configurazione
with open("impostazioni.json", "r") as f:
    dati = json.load(f)

if dati["verbose"] == "true":
    verbose = True
if dati["log_path"] != "":
    path = dati["log_path"]
if dati["max_results"] != "":
    maxResults = dati["max_results"]
if dati["api_url"] == "":
    print("Perfavore definire l'URL dell'API di SuiteCRM su impostazioni.json.")
    exit()
else:
    statics.baseUrl = dati["api_url"]

apiUsername = dati["api_username"]
apiPassword = dati["api_password"]
statics.moduleName = dati["module_name"]
query = dati["query"]

def main():
    analisiComando()
    configurazioneLog()
    #Autenticazione all'API
    statics.session = autenticazione()
    #Recupero messaggi non inviati dall'API
    data = collezione()
    ripartizione(data)
            
def analisiComando():
    args = sys.argv[1:]
    global path, verbose #Cambio lo scope a globale
    if len(args) == 2 and args[0] == "-v":
        path = args[1]
        verbose = True
    elif len(args) == 2 and args[1] == "-v":
        verbose = True
        path = args[0]
    elif len(args) == 1 and args[0] == "-v":
        verbose = True
    elif len(args) == 1:
        path = args[0]
    elif len(args) == 0:
        return
    else:
        print("Perfavore usa la sintassi corretta per eseguire il comando!")
        print("Utilizzo corretto: python3 inviaMessaggi.py [-v] [path]")
    
def autenticazione():
    logging.debug("Iniziata funzione autenticazione")
    
    loginurl = statics.baseUrl + """?method=login&input_type=JSON&response_type=JSON&rest_data={
            \"user_auth\":
                { 
                    \"user_name\":\"""" + apiUsername + """\",
                    \"password\":\"""" + apiPassword + """\"},
                    \"application_name\":\"\",
                    \"name_value_list\":{
                    \"name\":\"notifyonsave\",
                    \"value\":\"true\"}
                }
            """
        
    payload = {}
    headers = {}
    
    try:
        response = requests.request("GET", loginurl, headers=headers, data=payload)
        
    except HTTPError as http_err:
        logging.error(f'errore HTTP nel login: {http_err}')
        print(f'errore HTTP nel login: {http_err}')
        return -1
    
    except Exception as err:
        logging.error(f'errore generico nel login: {err}')
        print(f'errore generico nel login: {err}')
        return -1
    
    jsonResponse = response.json()
    
    try:
        id = jsonResponse["id"]
        
    except KeyError:
        logging.error(f'errore nel login: ' + response.text)
        print(f'errore nel login: ' + response.text)
        return -1
        
    print("Loggato correttamente con id sessione: " + id)
    logging.debug("Conclusa funzione autenticazione, l'id sessione è: " + id)
    return id
   
def collezione():
    dataurl = statics.baseUrl + """?method=get_entry_list&input_type=JSON&response_type=JSON&rest_data={
                    "session":\""""+ statics.session + """\",
                    "module_name":\"""" + statics.moduleName + """\",
                    "query":\"""" + query + """\",
                    "order_by":"",
                    "offset":0,
                    "select_fields":[],
                    "link_name_to_fields_array":{},
                    "max_result":""" + str(maxResults) +""",
                    "deleted":0
                }
            """    
    payload = {}
    headers = {}
    
    try:
        response = requests.request("GET", dataurl, headers=headers, data=payload)
        
    except HTTPError as http_err:
        logging.error(f'errore HTTP nella collezione: {http_err}')
        print(f'errore HTTP nella collezione: {http_err}')
        return -1
    
    except Exception as err:
        logging.error(f'errore generico nella collezione: {err}')
        print(f'errore generico nella collezione: {err}')
        return -1
    
    jsonResponse = response.json()
    
    try:
        resultCount = jsonResponse["result_count"]
        totalCount = jsonResponse["total_count"]
        
    except KeyError:
        logging.error(f'errore nella collezione: ' + response.text)
        print(f'errore nella collezione: ' + response.text)
        return -1
        
    print("Collezionati correttamente " + str(resultCount) + " su " + str(totalCount) + " messaggi non anccora mandati totali.")
    logging.info("Collezionati correttamente " + str(resultCount) + " su " + str(totalCount) + " messaggi non anccora mandati totali.")
    return jsonResponse

def configurazioneLog():
    
    if(verbose):
        tipolog = logging.DEBUG
    else:
        tipolog = logging.INFO
        
    logging.basicConfig(filename=path, level=tipolog,
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
    logging.info("Programma inizializzato con le seguenti flag: " + str(sys.argv[1:]))
    logging.debug("Verbose: " + str(verbose) + " Path: " + str(path) + " Risultati Massimi: " + str(maxResults))
    
main()