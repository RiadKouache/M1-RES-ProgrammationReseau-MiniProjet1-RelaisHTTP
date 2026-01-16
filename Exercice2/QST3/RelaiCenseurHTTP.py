from socket import *
import sys
import threading
import time
import os
import re # Pour les expressions régulières - Recommendation ChatGPT

def extract_get_uri(http_data):
    # Extraire l'URI d'une requête GET HTTP
    first_line = http_data.split('\r\n')[0]
    # Vérifier si c’est une requête GET
    if not first_line.startswith("GET"):
        print("Requête non GET, fermeture de la connexion.")
        return None
    else : 
        parts = first_line.split()
        if len(parts) >= 2:
            uri = parts[1]
            return uri
        else : 
            return None

def log_restricted_access(logfile, client_addr, uri, request=None):
    '''
    Log les accès restreints (censurés) dans le fichier de log
    appartenant au relai Sniffer. 
    Les deux relais (Sniffer et Censeur) partagent le même fichier de log.
    '''
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(logfile, "a", encoding="utf-8") as f:
        if request:
                uri = extract_get_uri(request)
                if uri:
                    f.write(f"[{timestamp}] CLIENT {client_addr[0]}:{client_addr[1]} → GET {uri} → BLOQUÉ {uri}\n")
        
def construct_blacklist(blacklist):
    if not os.path.exists(blacklist):
        print(f"Fichier de blacklist introuvable : {blacklist}")
        return []
    
    # Format du fichier de blacklist :
    reg_blacklist_req = re.compile(r"BLOCK_URI=(\S+)")

    with open(blacklist, "r", encoding="utf-8") as f:
        lignes = f.readlines() 
    
    uri_blocked = []

    for ligne in lignes : 
        uri_match = reg_blacklist_req.search(ligne)
        if uri_match : 
            blocked_uri = uri_match.groups()[0]
            uri_blocked.append(blocked_uri)
    
    return uri_blocked


def handle_client(clientSocket, addr,  SERVER_IP, SERVER_PORT, logfile, blocked_uris): 
    
    request = clientSocket.recv(4096).decode('utf-8')
    if not request:
        clientSocket.close()
        print("Pas de données reçues, fermeture de la connexion.")
        return
    
    uri = extract_get_uri(request)
    if not uri:
        clientSocket.close()
        return
        
    print(f"\n=== Analyse de l'URI : {uri} avec la Blacklist ===")
    if uri in blocked_uris:
        print(f"URI BLOQUÉE : {uri}. Envoi d'une réponse 403 Forbidden au client.")
        body = b"<html><head><title>403 Forbidden</title></head><body><h1>Acces confidentiel mon ami</h1></body></html>"
        
        # Construction complète du header HTTP
        forbidden_response = (
            "HTTP/1.1 403 Forbidden\r\n"
            f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())}\r\n"
            "Server: RelaiCenseurHTTP/1.0\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8')

        clientSocket.sendall(forbidden_response + body)
        log_restricted_access(logfile, addr, uri, request)
        clientSocket.close()
        return
    else:
        try :
            # L'URI n'est pas bloquée, on relaie la requête au serveur
                
            serveurSocket = socket(AF_INET, SOCK_STREAM)
            # Empecher un plantage si le serveur est injoignable - Recommendation ChatGPT
            try :   
                serveurSocket.connect((SERVER_IP, SERVER_PORT))
            except Exception as e:
                print(f"Erreur de connexion au serveur {SERVER_IP}:{SERVER_PORT} - {e}")
                clientSocket.close()
                return
            serveurSocket.sendall(request.encode('utf-8'))
            print(f"Requete transmise au serveur pour {uri}")
            # Lire la réponse complete du serveur 
            response = b""
            while True :
                data = serveurSocket.recv(4096)
                if not data :
                    break
                response += data
            # Envoyer la réponse au client
            clientSocket.sendall(response)
            serveurSocket.close()
        except Exception as e :
            print("Requête GET invalide")
            clientSocket.close()
            return
    clientSocket.close()
    print(f"Réponse envoyée pour {uri}")

def relaiCenseurHTTP(SERVER_IP, SERVER_PORT, LOCAL_PORT, logfile, blocked_uris): 
    '''
    Relai HTTP avec censure de certaines URI dans les requêtes GET.
    '''
    
    # Créer le socket d’écoute du relai
    relaisSocket = socket(AF_INET,SOCK_STREAM) 
    relaisSocket.bind(('',LOCAL_PORT))
    relaisSocket.listen(5) # file d'attente = 5 connexions
    print(f"Relai Censeur HTTP en écoute sur le port {LOCAL_PORT}... Serveur {SERVER_IP}:{SERVER_PORT}")
    
    while True : 
        clientSocket, addr = relaisSocket.accept()
        print(f"Client connecté : {addr}")
        
        thread = threading.Thread(target=handle_client, args=(clientSocket, addr,SERVER_IP, SERVER_PORT, logfile,blocked_uris), daemon=True) 
        thread.start()


if __name__ == "__main__":
    # Vérifie qu’on a bien 2 arguments (IP et port)
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <serveurHTTP_ip> <serveurHTTP_port>")
        sys.exit(1)

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])   
    LOCAL_PORT = 6000  # port d’écoute du relais
    LOG_FILE = os.path.abspath("./MiniProjet1/Exercice2/QST2/http_sniffer.log")
    BLACKLIST = os.path.abspath("./MiniProjet1/Exercice2/QST3/uri_blacklist.conf")
    blocked_uris = construct_blacklist(BLACKLIST)
    print(f"URIs bloquées : {blocked_uris}")

    relaiCenseurHTTP(SERVER_IP, SERVER_PORT, LOCAL_PORT, LOG_FILE, blocked_uris)
