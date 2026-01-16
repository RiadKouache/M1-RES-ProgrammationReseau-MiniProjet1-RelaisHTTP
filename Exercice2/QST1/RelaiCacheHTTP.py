from socket import *
import sys
import threading

def handle_client(clientSocket, SERVER_IP, SERVER_PORT, cache): 
    
    request = clientSocket.recv(4096).decode('utf-8')
    if not request:
        clientSocket.close()
        print("Pas de données reçues, fermeture de la connexion.")
        return
    
    # Extraire la ligne de commande HTTP 
    first_line = request.split('\r\n')[0]
    print(f"Requête reçue : {first_line}")

    # Vérifier si c’est une requête GET
    if not first_line.startswith("GET"):
        print("Requête non GET, fermeture de la connexion.")
        clientSocket.close()
        return
    else :
        parts = first_line.split()
        if len(parts) >= 2:
            uri = parts[1]
            print(f"URI demandée : {uri}")

            if uri in cache :
                print(f"Réponse trouvée dans le cache pour {uri}")
                response = cache[uri] 
                clientSocket.sendall(response)
                print(f"Requete transmise au serveur pour {uri}")
            else : 
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
                # Stocker dans le cache
                # Stocker dans le cache si code 200 OK - Recommendation ChatGPT
                if b"200 OK" in response.split(b"\r\n")[0] :
                    cache[uri] = response
                    print(f"Réponse mise en cache ({len(response)} octets)")
                else :
                    print(f"Réponse non mise en cache (code != 200)")
                # Envoyer la réponse au client
                clientSocket.sendall(response)
                serveurSocket.close()
        else : 
            print("Requête GET invalide")
            clientSocket.close()
            return
        
    clientSocket.close()
    print(f"Réponse envoyée pour {uri}")


def relaiHTTP(SERVER_IP, SERVER_PORT, LOCAL_PORT):
    
    cache = {}

    relaisSocket = socket(AF_INET, SOCK_STREAM)
    relaisSocket.bind(('', LOCAL_PORT))
    relaisSocket.listen(5) # file d'attente = 5 connexions
    print(f"Relai HTTP prêt sur le port {LOCAL_PORT} -> Serveur {SERVER_IP}:{SERVER_PORT}")

    while True:
        clientSocket, addr = relaisSocket.accept()
        print(f"Client connecté : {addr}")

        thread = threading.Thread(target=handle_client, args=(clientSocket, SERVER_IP, SERVER_PORT, cache), daemon=True) 
        thread.start()


if __name__ == "__main__":
    # Vérifie qu’on a bien 2 arguments (IP et port)
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <serveurHTTP_ip> <serveurHTTP_port>")
        sys.exit(1)

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])   
    LOCAL_PORT = 5000  # port d’écoute du relais

    relaiHTTP(SERVER_IP, SERVER_PORT, LOCAL_PORT)