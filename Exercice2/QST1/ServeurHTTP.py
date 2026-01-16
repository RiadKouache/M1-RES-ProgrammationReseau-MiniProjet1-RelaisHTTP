from socket import *
import sys 
import os 
import mimetypes
import urllib.parse # Pour décoder les %xx dans les URLs (meme si les URLs sont simples cela reste une bonne pratique) - Recommendation ChatGPT
import time 

DOCUMENT_ROOT = os.path.abspath("./MiniProjet1/Exercice2/QST1")  # répertoire courant

# Construire les headers HTTP - Fonction tirée de mon TME1 (serveur web basique)
def build_headers(status_code, status_text, content_length, content_type="text/html; charset=utf-8") :
    headers = f"HTTP/1.1 {status_code} {status_text}\r\n" ## status_code/status_text représente le message http exp :200 OK
    headers += f"Date: {time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())}\r\n" # Date actuelle au format HTTP
    headers += "Server: SimplePythonHTTPServer/1.0\r\n"
    headers += f"Content-Length: {content_length}\r\n" # Pour avoir la taille du body en octets 
    headers += f"Content-Type: {content_type}\r\n" # Pour indiquer le type MIME (format envoyé) du body; ex :text/html
    headers += "Connection: close\r\n" # Indique que le serveur ferme la connexion après avoir envoyé la réponse
    headers += "\r\n" # Fin des headers, début du body
    return headers.encode('utf-8')

def handle_req(conn, addr) :
    try : 
        conn.settimeout(5)  # timeout de 5 secondes
        request = ("").encode('utf-8')
        while ("\r\n\r\n").encode('utf-8') not in request : # séquence \r\n\r\n = fin des headers HTTP
            data = conn.recv(4096) # lire les données recues
            if not data : 
                break
            request += data 
        if not request : 
            print(f"[{addr}] no data received")
            return 
        
        # Decodage de la requete HTTP 
        request_text = request.decode('iso-8859-1') 
        first_line = request_text.splitlines()[0]
        parts = first_line.split() 

        # Extraire le chemin (sans query) et décoder %xx en espace par exp
        path = urllib.parse.unquote(parts[1].split('?', 1)[0]) 
        if path == '/' : # la racine du site est index.html
            path = "/index.html"

        safe_path = path.lstrip("/") 
        # Construire le chemin absolu du fichier demandé
        requested_file = os.path.normpath(os.path.join(DOCUMENT_ROOT , safe_path))
        print(f"[{addr}] requested file: {requested_file}")
        
        # Si le fichier existe : l'envoyer ; sinon envoyer error404.html si présent ou message 404
        if os.path.isfile(requested_file) :
            filesize = os.path.getsize(requested_file)
            ctype, _ = mimetypes.guess_type(requested_file) 
            headers = build_headers(200, "OK", filesize, content_type=ctype)
            conn.sendall(headers)
            with open(requested_file, 'rb') as f :
                while True :
                    dataFile = f.read(4096)
                    if not dataFile :
                        break
                    conn.sendall(dataFile)
                    print(f"Response sent for : {requested_file}")

        # Fichier manquant : Envoyer un HTML avec 404 Not Found
        else : 
            # pas de error404.html, envoyer un message simple
            body = b"<h1>404 Not Found</h1>"
            headers = build_headers(404, "Not Found", len(body), "text/html; charset=utf-8")
            conn.sendall(headers + body)  
            print(f"Error 404 sent for : {requested_file}")
          
        
    except timeout :
        print(f"[{addr}] timeout... ")

    finally :
        conn.close()    

def serverHTTP(IpAddress,serverport) : 

    serverSocket = socket(AF_INET,SOCK_STREAM) 
    serverSocket.bind((IpAddress,serverport))
    serverSocket.listen(5) # file d'attente = 3 connexion
    print(f"HTTP Server running on {IpAddress}:{serverport}, docroot={DOCUMENT_ROOT} ")

    while True : 

        connectionSocket, Address = serverSocket.accept()
        print("Connection from", Address)
        handle_req(connectionSocket, Address)

if __name__ == "__main__":
    # Vérifie qu’on a bien 2 arguments (IP et port)
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <IpAddress> <Port>")
        sys.exit(1)

    IpAddress = sys.argv[1]
    serverport = int(sys.argv[2])   # convertir en entier
    serverHTTP(IpAddress, serverport)