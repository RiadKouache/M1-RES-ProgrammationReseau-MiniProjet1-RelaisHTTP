from socket import *
import sys
import threading

def handle_client(clientSocket, addr, SERVER_IP, SERVER_PORT): 
    try:
        serveurSocket = socket(AF_INET, SOCK_STREAM)
        serveurSocket.connect((SERVER_IP, SERVER_PORT))

        while True : 
            data = clientSocket.recv(2048) 
            if not data:
                break

            serveurSocket.sendall(data)
            reponse = serveurSocket.recv(2048)
            if not reponse:
                break
            clientSocket.sendall(reponse)
    finally:
        clientSocket.close()
        serveurSocket.close()
        print(f"Connexion avec le client {addr} terminée.\n")

def relaiTCP(SERVER_IP, SERVER_PORT, LOCAL_PORT):
    
    relaisSocket = socket(AF_INET, SOCK_STREAM)
    relaisSocket.bind(('', LOCAL_PORT))
    relaisSocket.listen(3) # file d'attente = 3 connexions
    print(f"Relai TCP prêt sur le port {LOCAL_PORT} -> Serveur {SERVER_IP}:{SERVER_PORT}")

    while True:
        clientSocket, addr = relaisSocket.accept()
        print(f"Client connecté : {addr}")

        thread = threading.Thread(target=handle_client, args=(clientSocket, addr, SERVER_IP, SERVER_PORT), daemon=True) 
        thread.start()

if __name__ == "__main__":
    # Vérifie qu’on a bien 2 arguments (IP et port)
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <serveur_ip> <serveur_port>")
        sys.exit(1)

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])   
    LOCAL_PORT = 5000  # port d’écoute du relais

    relaiTCP(SERVER_IP, SERVER_PORT, LOCAL_PORT)