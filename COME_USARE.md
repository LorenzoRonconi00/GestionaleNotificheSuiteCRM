### Installazione Dipendenze

1 - Installare python e controllare che il comando 'pip' funzioni. 
(Potrebbe essere necessario riavviare il terminale dopo l'installazione)

2 - Aprire un terminale sulla cartella del progetto (../SuiteCRM-Messenger), eseguire il seguente comando:
pip install -r .\requirements.txt

### Configurazione Dati

#### Usando il file 'impostazioni.json', inserire le informazioni necessarie al funzionamento del programma.

**verbose** : "true" o "false"  
indica se l'output nei log debba essere piu' dettagliato, per motivi di debugging

**log-path** : "" o "path-relativo/nomefile.estenzione" o "path-assoluto/nomefile.estensione"  
indica dove deve essere salvato il file di log.

**max-results** : numero  
Numero di risultati che il programma ottiene dal CRM ad ogni ciclo di esecuzione.

**api_url** : "URL"
Url dell'API di suitecrm.
Esempio: "https://testkeyall.cittadigitale.org/service/v4/rest.php"

**email_sender** : "email"  
Email da cui inviare i messaggi.

**email_password** : "password"  
Password API della mail da cui mandare i messaggi.

**skebby_email** : "email"  
Email di Skebby da usare per mandare gli SMS   

**skebby_password** : "password"  
Password dell'account Skebby

### Esecuzione Programma

Per eseguire il programma, aprire il terminale sulla cartella del progetto (../SuiteCRM-Messenger)
ed eseguire il seguente comando: 

python3 inviaMessaggi.py (-v) (logpath)

**-v** : Indica se abilitare il verbose. in caso la flag non sia presente, il programma sceglie di default l'opzione nelle impostazioni.json.

**logpath** Stessa cosa: qui si puo' scegliere un path alternativo per i log, ma se non e' specificato, il programma sceglie di default quello definito in impostazioni.json.


### FILE MAIL.PY ###

Il file mail.py si occupa dell'invio mail tramite protocollo SMTP (modulo smtplib) e modulo SSL per mantenere una connessione sicura. 

-Moduli:
    1. EmailMessage dal pacchetto email.message per creare un oggetto EmailMessage che sará l'email da inviare
    2. Update dal pacchetto util.updateMessage per aggiornare il corretto invio del messaggio su Suite
    3. Ssl, smtplib e logging rispettivamente per gestire una connessione sicura, inviare l'email e registrare gli eventi
 
 -Funzionamento:
 
 1. Logger --> creato tramite modulo logging
    Context --> creato tramite il comando create_default_context() per stabilire una connessione sicura

 2. invia_mail():
      -definita con i parametri specificati per poi essere passati dalla funzione ripartizione()
      -dopo aver creato l'oggetto "em" (EmailMessage) e avergli passato i campi definiti della dichiarazione della funzione, andiamo a stabilire la connessione con il server
       SMTP di Gmail tramite porta "465"
      -Effettuiamo il login all'account Gmail del mittente, tramite comando login(), per poi inviare la mail tramite metodo sendmail() con l'oggetto "em" convertito in stringa
      -Tutto ció é gestito da un try per gestire eventuali eccezioni e, nel caso ci siano, viene registrato tutto nel file di log
      -Infine viene eseguito l'update del corretto invio del messaggio, sempre il tutto gestito da eventuali eccezioni
     

### FILE SMS.PY ###

Il file sms.py si occupa dell'invio di messaggi utilizzando l'API di Skebby.

-Moduli: 
  1. Requests per le richieste HTTP (ricordarsi di installare requests tramite comando 'pip install requests')
  2. Json per manipolare dati json in python
  3. Sys per la gestione del tempo
  4. Datetime per gestire il flusso di output
  5. Logging per registrare gli eventi

-Funzionamento:

1. Logger --> create tramite modulo logging
   BASEURL --> per le richieste all'API di Skebby
   MESSAGGE_HIGH_QUALITY ecc.. --> costanti per la qualitá del messaggio

2. json_serial():
      -serializzazione degli oggetti, definiti della dichiarazione della funzione, in formato json 

3. login():
      -per autenticarsi all'API di Skebby utilizzando username e password, definiti nella dichiarazione della funzione. La funzione effettua una richiesta GET all'API 
       e, se con successo, restituisce "user_key" e "session_key". Nel caso contrario viene restituito None

4. sendSMS():
      -prende in input l'auth (user_key, session_key), il messaggio da inviare, destinatario e mittente
      -crea un dizionario "sendsms" con i dati da inviare all'API come messaggio, qualitá di invio, destinatario, mittente ed eventuali ulteriori parametri
      -effettua una richiesta POST all'API passando i dati come payload JSON nell'header della richiesta. Se tutto ció non va a buon fine, viene registrato un messaggio 
       di errore nel registro
       
       

### FILE UPDATEMESSAGE.PY ###

Semplice file di aggiornamento invio del messaggio (mail, sms) tramite API REST. In particolare viene definita la variabile "updateurl" come url dell'endpoint di 
aggiornamento dell'API, concatenando costanti (stringhe), definite nel modulo statics, l'ID e ulteriori dati JSON che specificano sessione, nome modulo e valori dei campi da 
aggiornare (is_sent). Il tutto é gestito da un try-except per gestire eventuali errori durante la richiesta HTTP


### FILE RIPARTIZIONE.PY ###

Il file ripartizione.py si occupa della gestione delle notifiche

-Moduli:
  1. Json --> per il parsing JSON
  2. Threading --> gestione dei thread
  3. asyncio --> esecuzione asincrona
  4. util.sms --> utilizzo del modulo sms
  5. util.mail --> utilizzo del modulo mail
  6. logging --> registrazione degli eventi
  7. concurrent.futures --> esecuzione concorrente

-Funzionamento:

  1. Dopo aver creato l'oggetto logger per la registrazione degli eventi nel file log, viene aperto il file "impostazioni.json" per l'utilizzo dell'indirizzo mail mittente, 
     password mail, indirizzo mail Skebby e password Skebby
  2. La funziona asincrona ripartizione() gestisce la ripartizione dei messaggi per l'invio tramite SMS o Email, dove i messaggi vengono estratti dal campo 'entry_list' del parametro
     "data" definito nella dichiarazione della funzione. 
  3. Se l'autenticazione a Skebby é stata effettuamente correttamente, viene creato un thread pool con un massimo di 3 workers e un elenco di oggetti "futures" per le operazioni di invio
     dei messaggi. Per ogni messaggio nella lista 'messages' viene invocata "sendMsg" tramite comando executor.submit()
  4. Dopo l'attessa del completamento degli oggetti "Future", vengono salvati i risultati in una lista chiamata "results" per poi stampare il numero di messaggi inviati correttamente
  5. La funzione sendMsg() prende come parametro il messaggio e controlla il tipo di notifica specificato nel messaggio, richiamando la funzione corrispondente al tipo (sms, mail). 
     Se l'autenticazione a Skebby non é andata a buon fine, viene registrato un errore di autenticazione o di errore generico
  6. La funzione main() avvia semplicemente l'esecuzione della funzione ripartizione() tramite asyncio.run
