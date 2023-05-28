import json
import threading
import asyncio
import util.sms
import util.mail
import logging
import concurrent.futures
logger = logging.getLogger(__name__)

with open("impostazioni.json", encoding="UTF-8") as f:
    impostazioni = json.load(f) 
    mittente = impostazioni['email_sender']
    password = impostazioni['email_password']
    authSkebby = util.sms.login(impostazioni['skebby_email'], impostazioni['skebby_password'])
    
async def ripartizione(data):
    messages = data['entry_list']
    
    if authSkebby is None:
        print("Errore nell'autenticazione Skebby, sara' impossibile inviare gli SMS")
        logger.error("Errore nell'autenticazione Skebby, impossibile inviare gli SMS")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit 5 tasks to the thread pool
        futures = [executor.submit(sendMsg, msg) for msg in messages]
    
    results = [future.result() for future in futures]
    print("Mandati correttamente " + str(sum(results)) + " su " + str(len(messages)) + " messaggi")

def sendMsg(msg):
    if msg['name_value_list']['notification_type']['value'] == 'EMAIL':
        return util.mail.invia_mail(mittente, 'federicocervelli01@gmail.com', msg['name_value_list']['subject']['value'], msg['name_value_list']['body']['value'], password, msg["id"])
    elif msg['name_value_list']['notification_type']['value'] == 'SMS' and authSkebby is not None:
        return util.sms.sendSMS(authSkebby, msg['name_value_list']['body']['value'], "+393661455735", None)
    else:
        if authSkebby == None:
            logging.error("Impossibile inviare SMS, autenticazione Skebby fallita")
            return 0
        logging.error("Errore generico invio messaggio ")
        return 0

def main(data):
    asyncio.run(ripartizione(data))
    
