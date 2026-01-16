from socket import *

serverName = '127.0.0.1'
serverPort = 5000  # port du RELAY
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
message = input('Phrase à envoyer :').encode('utf-8')
clientSocket.send(message)
modified = clientSocket.recv(2048).decode('utf-8')
print('Reçu :', modified)
clientSocket.close()