#!/usr/bin/python

"""
Authors:
    Augusto Melo.
    Danilo Ikeda.
    Gustavo Silva.
"""

import socket
import sys
import os.path 

CUR_DIR = '.'

HOST = '127.0.0.1'
PORT = 0

BUFFER  = 10000

DEFAULT_HTML = "/index.html"
NOT_FOUND404 = "notfound404.html"

HTTP200 = "\nHTTP/1.1 200 OK\n"
HTTP404 = "\nHTTP/1.1 404 Not Found\n"
CONTENTTYPE = "Content-Type: text/html\n\n" 

def sendFile(conn, filePath):
    """
    Send a file trought the socket.
    
    Args:
        conn: Socket connection
        filePath: The file requested
    Raises:
        IOErros: Problem using the file.
    """
    try:
        file = open(filePath)
        content = file.read(BUFFER)

        while(content):
            conn.sendall(content.encode())
            content = file.read(BUFFER)

        file.close()

    except IOError as err:
        print("Problem during the IO processing.", format(err))


def verifyRequest(conn, filePath):
    """
    Verify request made by the client.
    
    Args:
        conn: Socket connection
        filePath: The file requested
    """
    if (not(os.path.isfile(filePath))):
        # Try to find default html page.
        print(filePath)
        filePath += DEFAULT_HTML
        if (not(os.path.isfile(filePath))):
            # Send http 404
            conn.sendall(HTTP404.encode())
            conn.sendall(CONTENTTYPE.encode())

            sendFile(conn, NOT_FOUND404)

            return

            
    conn.sendall(HTTP200.encode())
    conn.sendall(CONTENTTYPE.encode())

    sendFile(conn, filePath)


def main():
    # Verify the number of arguments.
    if(len(sys.argv) == 1):
        print("You have to pass a port as an argument.")
        return 1

    PORT = int(sys.argv[1])

    print("Starting server on: " + str(PORT) + ".")
    
    # Create a inet, and streaming socket. 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Tells the kernel to reuse the socket.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)


    while True:
        conn, addr = sock.accept()
        client = (conn.recv(BUFFER)).decode('utf-8')

        # Doing this we have an array with the requisitation.
        # [0] => HTTP Method.
        # [1] => File requisitation.
        # [2] => HTTP version.
        # ...
        client = client.split(' ')

        if (client[0] == 'GET'):
            # Send response.
            verifyRequest(conn, CUR_DIR + client[1])

        conn.close()


if __name__ == "__main__":
    main()
