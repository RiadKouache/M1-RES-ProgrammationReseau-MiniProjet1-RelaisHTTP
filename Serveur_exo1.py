from socket import *

serverPort = 6000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(3)
print(f'Serveur prêt sur le port {serverPort} ...')


while True:
    connectionSocket, addr = serverSocket.accept()
    message = connectionSocket.recv(2048).decode('utf-8')
    modified = message.upper().encode('utf-8')
    connectionSocket.send(modified)
    connectionSocket.close()

