from util import statics
import requests
import logging
logger = logging.getLogger(__name__)

def update(id):
    updateurl = statics.baseUrl + """?method=set_entry&input_type=JSON&response_type=JSON&rest_data=
        {
            "session" : \"""" + statics.session + """\",
            "module-name" : \"""" + statics.moduleName + """\",
            "name-value-list" : {
                "id" : {
                    "name" : "id",
                    "value" : \"""" + id + """\"
                },
                "is_sent": {
                    "name" : "is_sent",
                    "value" : 1
                }
            }
        }
    """
    
    payload = {}
    headers = {}
    
    try:
        response = requests.request("GET", updateurl, headers=headers, data=payload)
        
    except requests.HTTPError as http_err:
        logging.error(f'errore HTTP nell\'aggiornamento: {http_err}')
        print(f'errore HTTP nell\'aggiornamento: {http_err}')
        return 0
    
    except Exception as err:
        logging.error(f'errore generico nell\'aggiornamento: {err}')
        print(f'errore generico nell\'aggiornamento: {err}')
        return 0
    
    if(response.status_code != 200):
        logger.error(f'errore nell\'aggiornamento: {response.text}')
        return 0
    
    return 1
    