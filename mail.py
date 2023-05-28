from email.message import EmailMessage
from util.updateMessage import update
#tecnologia standard per mantenere una connessione internet sicura per tenere riservati i dati sensibili
import ssl
#per mandare la mail
import smtplib
import logging

logger = logging.getLogger(__name__)

context = ssl.create_default_context()
#specifichiamo prima il servizio con la quale spediamo la mail (gmail)

def invia_mail(mittente, destinatario, oggetto, descrizione, password, messageid):
    try:
        em = EmailMessage()
        em['From'] = mittente
        em['To'] = destinatario
        em['Subject'] = oggetto
        em.set_content(descrizione)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(mittente, password)
            smtp.sendmail(mittente, destinatario, em.as_string())
        logger.debug("Inviata correttamente la mail a " + destinatario)
    except Exception as e:
        logger.error("Errore invio mail a " + destinatario + ": " + str(e))
        return 0
    
    try:
        update(messageid)
    except Exception as e:
        logger.error("Errore aggiornamento messaggio " + messageid + ": " + str(e))
        return 0
    return 1