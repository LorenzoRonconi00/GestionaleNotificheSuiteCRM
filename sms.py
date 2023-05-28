# pip install requests
import requests
import json
import sys
import datetime
import logging

logger = logging.getLogger(__name__)

BASEURL = "https://api.skebby.it/API/v1.0/REST/"

# Qualita del messaggio da specificare poi nel main
MESSAGE_HIGH_QUALITY = "GP"
MESSAGE_MEDIUM_QUALITY = "TI"
MESSAGE_LOW_QUALITY = "SI"


def json_serial(obj):
    # Serializzazione in formato json dell'oggetto inviaSMS per trasmetterlo tramite richiesta HTTP POST all'API

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

    raise TypeError ("Type not serializable")

def login(username, password):
    # Ritorna una coppia (user_key, session_key) dopo l'autenticazione

    r = requests.get("%slogin?username=%s&password=%s"
                     % (BASEURL, username, password))

    if r.status_code != 200:
        print("--Errore : Impossibile effettuare il Login--")
        return None

    user_key, session_key = r.text.split(';')
    print("--Autenticazione effettuata : Login riuscito--")
    return user_key, session_key

def sendSMS(auth, message, recipient, sender):
    try:
        sendsms =   {
                        # Messaggio da inviare
                        "message" : message,
                        # Qualitá del messaggio dichiarata all'inizio
                        "message_type" : MESSAGE_HIGH_QUALITY,
                        "returnCredits" : False,
                        # Numero destinatario
                        "recipient": [recipient,],
                        # Mittente custom
                        "sender": sender,
                        # Posticipare l'invio in minuti
                        "scheduled_delivery_time" : None
                    }  
        headers = { 'user_key': auth[0],
                    'Session_key': auth[1],
                    'Content-type' : 'application/json' }
        # Json.dumps() converte l'oggetto sendsms in stringa json prima di includerlo nella richiesta HTTP POST
        r = requests.post("%ssms" % BASEURL,
                        headers=headers,
                        data=json.dumps(sendsms, default=json_serial))

        # Converte la stringa json in oggetto python
        response = json.loads(r.text)
        if response['result'] == "OK":
            return 1
        else:
            logger.error("Errore nell'invio dell'SMS: " + response['result'])
            return 0
    except Exception as e:
        logger.error("Errore nell'invio dell'SMS: " + str(e))
        return 0