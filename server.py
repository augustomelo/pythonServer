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
import json

HOST = '127.0.0.1'
PORT = 0

BUFFER  = 10000

DEFAULT_HTML = "/index.html"
NOT_FOUND404 = "notfound404.html"

HTTP200 = "\nHTTP/1.1 200 OK\n"
HTTP201 = "\nHTTP/1.1 201 Created\n"
HTTP204 = "\nHTTP/1.1 204 No Content\n"
HTTP404 = "\nHTTP/1.1 404 Not Found\n"
CONTENTTYPE = "Content-Type: text/html\n\n" 

def sendFile(conn, filePath):
    """
    Send a file trought the socket.
    
    Args:
        conn: Socket connection.
        filePath: The file requested.
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


def GETRequest(conn, filePath):
    """
    Send a response to a GET request.
    
    Args:
        conn: Socket connection.
        filePath: The file requested.
    """
    if (not(os.path.isfile(filePath))):
        # Try to find default html page.
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


def POSTRequest(conn, resource, values, dic):
    """
    Send a response to a POST request.

    Args:
       conn: Socket connection. 
       resource: What the client is trying to reach.
       values: The value that the client wants to insert.
       dic: A dictionary with resorces and values.
    """
    create = False 
    resource = resource.split('/')
    resource = resource[1:]

    graph = resource[0]
    
    if (values != 'NULL'):
        values = values.split('=')
        values[0] = resource[-1]

        if (len(values) == 2):
            if (values[0] not in dic[graph]['pesos']):
                create = True
            dic[graph]['pesos'][values[0]] = values[1]

        else:
            conn.sendall(HTTP204.encode())
            return
    
    else:
        if(graph not in dic):
            dic[graph] = {}
            dic[graph]['arestas'] = []
            dic[graph]['pesos'] = {}
            create = True

        for edge in resource[1:]:
            if (edge not in dic[graph]['arestas']):
                create = True
            dic[graph]['arestas'].append(edge)

    if (create):
        conn.sendall(HTTP201.encode())

    else:
        conn.sendall(HTTP200.encode())

def removeAllOccurence(graph, edge, dic):
    """
    Remove all occurence of an edge form the dictionary.

    Args:
       graph: Graph that is going to be removed.
       edge: Edge that is going to be removed.
       dic: Where is the information to be removed.
    """
    for key in list(dic[graph]['pesos'].keys()):
        if (edge in key):
            del(dic[graph]['pesos'][key])

def DELETERequest(conn, resource, dic):
    """
    Send a response to a POST request.

    Args:
       conn: Socket connection. 
       resource: What the client is trying to reach.
       dic: A dictionary with resorces and values.
    """
    resource = resource.split('/')
    resource = resource[1:]
    graph = resource[0]

    # Remove the edge and all its weigth.
    if(len(resource) == 2):
        if(resource[1] in dic[graph]['arestas']):
            index = dic[graph]['arestas'].index(resource[1])
            del(dic[graph]['arestas'][index])
            removeAllOccurence(graph, resource[1], dic)
            conn.sendall(HTTP200.encode())

        else:
            conn.sendall(HTTP204.encode())

            return

    # Remove all the graph.
    else:
        if (graph in dic):
            del(dic[graph])
            conn.sendall(HTTP200.encode())
            
            return

        else:
            conn.sendall(HTTP204.encode())
    

def main():
    # Verify the number of arguments.
    if(len(sys.argv) == 1):
        print("You have to pass a port as an argument.")
        return 1

    PORT = int(sys.argv[1])
    CUR_DIR  = '.' if(len(sys.argv) == 2) else sys.argv[2]
    dic = {}

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
        fullrequest = client.split('\r\n')
        fullrequest = list(filter(None, fullrequest))
        fullrequest = fullrequest[0].split(' ') + fullrequest[1:]

        if (fullrequest[0] == 'GET'):
            GETRequest(conn, CUR_DIR + fullrequest[1])

        elif (fullrequest[0] == 'POST' or fullrequest[0] == 'PUT'):
            POSTRequest(conn, fullrequest[1], fullrequest[-1], dic)

        elif (fullrequest[0] == 'DELETE'):
            DELETERequest(conn, fullrequest[1], dic)

        print(json.dumps(dic))

        conn.close()


if __name__ == "__main__":
    main()


