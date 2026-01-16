from socket import *
import sys
import threading
import time
import os

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


def log_http(logfile, client_addr, request=None, response=None): 
    '''
    On doit avoir assez d'info pour faire un audit : 
    - Log file : chemin du fichier de log 
    - client_addr : adresse IP et port du client
    - request : la requête HTTP complète 
    - response : la réponse HTTP complète 
    '''
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    with open(logfile, "a", encoding="utf-8") as f:
        if request:
            uri = extract_get_uri(request)
            if uri:
                f.write(f"[{timestamp}] CLIENT {client_addr[0]}:{client_addr[1]} → GET {uri}\n")
        
        if response:
            if len(response.strip())>0: 
                try : 
                    first_line = response.decode("iso-8859-1", errors="ignore").split("\r\n")[0]
                    parts = first_line.split()
                    code = parts[1] if len(parts) >= 2 else "?"
                    f.write(f"[{timestamp}] SERVEUR → {client_addr[0]}:{client_addr[1]} | {first_line} | taille={len(response)}\n")
                    f.write(f"Réponse (décodée) :\n{response.decode('utf-8', errors='ignore')}\n\n")
                except Exception:
                    f.write(f"[{timestamp}] SERVEUR → {client_addr[0]}:{client_addr[1]} | Réponse non décodable ({len(response)} octets)\n")
                    


def handle_client(clientSocket, addr,  SERVER_IP, SERVER_PORT, logfile): 
    
    request = clientSocket.recv(4096).decode('utf-8')
    if not request:
        clientSocket.close()
        print("Pas de données reçues, fermeture de la connexion.")
        return
    
    else :
        try :
            uri = extract_get_uri(request)
            
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
                
            log_http(logfile, addr, request, response)
            print(f"Réponse reçue du serveur pour {uri}, taille={len(response)} octets")
            
            # Envoyer la réponse au client
            clientSocket.sendall(response)
            serveurSocket.close()
        
        except Exception as e : 
            print("Requête GET invalide")
            clientSocket.close()
            return
        
    clientSocket.close()
    print(f"Réponse envoyée pour {uri}")


def relaiSnifferHTTP(SERVER_IP, SERVER_PORT, LOCAL_PORT, logfile):
    

    relaisSocket = socket(AF_INET, SOCK_STREAM)
    relaisSocket.bind(('', LOCAL_PORT))
    relaisSocket.listen(5) # file d'attente = 5 connexions
    print(f"Relai Sniffer HTTP prêt sur le port {LOCAL_PORT} -> Serveur {SERVER_IP}:{SERVER_PORT}")

    while True:
        clientSocket, addr = relaisSocket.accept()
        print(f"Client connecté : {addr}")
        
        thread = threading.Thread(target=handle_client, args=(clientSocket, addr,SERVER_IP, SERVER_PORT, logfile), daemon=True) 
        thread.start()


if __name__ == "__main__":
    # Vérifie qu’on a bien 2 arguments (IP et port)
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <serveurHTTP_ip> <serveurHTTP_port>")
        sys.exit(1)

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])   
    LOCAL_PORT = 7000  # port d’écoute du relais
    LOG_FILE = os.path.abspath("./MiniProjet1/Exercice2/QST2/http_sniffer.log")

    relaiSnifferHTTP(SERVER_IP, SERVER_PORT, LOCAL_PORT, LOG_FILE)