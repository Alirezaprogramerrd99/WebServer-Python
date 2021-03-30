from socket import *
import os.path, time

serverSocket = socket(AF_INET, SOCK_STREAM)  # using TCP protocol in transport layer.
server_Hostname = gethostname()
ip_address = gethostbyname(server_Hostname)
print("working on %s with IP-Address (%s)" % (server_Hostname, ip_address))  # printing server info.

# when anyone sends a packet to port 12345 at the IP address of the server(ip_address), that packet will be
# directed to this socket.

SERVER_PORT = 5050  # Reserve a port for your service.
FORMAT = 'utf-8'
serverSocket.bind((ip_address, SERVER_PORT))  # Bind to the port
serverSocket.listen(1)  # waiting for new requests.
filename = ''
fileFormat = ''
outputdata = None

try:
    while True:
        # Establish the connection...
        connectionSocket, client_address = serverSocket.accept()

        # after establishing connection, serverSocket, which creates a
        # new socket in the server(our process) connectionSocket and returns
        # the information of the client(ip-address and clients port number)

        try:
            print('Got connection from client ', client_address)
            message = connectionSocket.recv(1024).decode(FORMAT)  # recv 1024 bytes from client.

            if message:
                filename = message.split()[1]
                filename = filename[1:]    # do we must check if the file name was favicon.ico close the socket or continue the loop

                if filename:     # for cases that user just want simple connection.
                    fileFormat = filename[1:].split('.')[1]

            print("\nrequest massage: " + message)
            print("filename: " + filename)

            #------ handling headers for HTTP response to client

            if fileFormat and fileFormat != 'ico':    # we dont proccess (.ico) file (ignore it).

                if fileFormat == 'html':
                    fileObject = open(filename, 'r')
                    outputdata = fileObject.read()


                    connectionSocket.send('\nHTTP/1.1 200 OK\n'.encode(FORMAT))
                    connectionSocket.send(('Server: ' + server_Hostname + '\n').encode(FORMAT))
                    connectionSocket.send('Content-Type: text/html; charset=utf-8\n'.encode(FORMAT))
                    connectionSocket.send('Connection: Keep-Alive;\n\n'.encode(FORMAT))

                    connectionSocket.sendall(outputdata.encode())
                    connectionSocket.send("\r\n".encode())

                if fileFormat == 'jpg':
                    fileObject = open(filename, 'rb')
                    connectionSocket.send('\nHTTP/1.1 200 OK\n'.encode(FORMAT))
                    connectionSocket.send(('Server: ' + server_Hostname + '\n').encode(FORMAT))
                    connectionSocket.send('Content-Type: multipart/form-data; \n'.encode(FORMAT))
                    connectionSocket.send('Connection: Keep-Alive;\n\n'.encode(FORMAT))

                    while 1:
                        outputdata = fileObject.readline(512)   # we read every 512 bytes of data from src jpeg file.
                        if not outputdata:           # if file was not ended.
                            break
                        connectionSocket.sendall(outputdata)

                    #connectionSocket.send( ('Last-Modified: ' + time.ctime(os.path.getmtime(f.name)) + '\n').encode(FORMAT) )

                # for i in range(0, len(outputdata)):
                #     connectionSocket.send(outputdata[i].encode())
                # connectionSocket.send("\r\n".encode())

            connectionSocket.close()

        except (IOError, FileNotFoundError):

            print('file not found!!')
            fileObject = open('fileNotFound.html')
            error_data = fileObject.read().encode(FORMAT)

            connectionSocket.send('\nHTTP/1.1 404 not found\n\n'.encode(FORMAT))
            connectionSocket.sendall(error_data)
            connectionSocket.close()

finally:
    serverSocket.close()
    print('server shut down.')
