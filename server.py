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
import select

HOST = '127.0.0.1'
PORT = 0

BUFFER  = 10000

DEFAULT_HTML = "/index.html"
NOT_FOUND404 = "notfound404.html"

HTTP200 = "\nHTTP/1.1 200 OK\n"
HTTP201 = "\nHTTP/1.1 201 Created\n"
HTTP204 = "\nHTTP/1.1 204 No Content\n"
HTTP404 = "\nHTTP/1.1 404 Not Found\n"
HTTP400 = "\nHTTP/1.1 400 Bad Request\n"
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

def sendInfoEdge(conn, vertex, dic):
    """
    Send all the information about the vertex.

    Args:
        conn: Socket connection.
        vertex: Edge that is going to be printed.
        dic: Graph dictionary with the information.
    """

    tempDic = {}
    tempDic["pesos"] = {}
    
    for key, value in list(dic['pesos'].items()):
        if (vertex in key):
            tempDic["pesos"][key] = value


    # Send the information
    conn.sendall(HTTP200.encode())
    conn.sendall(json.dumps(tempDic).encode())

    del(tempDic)


def sendGraph(conn, filePath, dic):
    """
    Send a graph to the client.
    
    Args:
        conn: Socket connection.
        filePath: The file requested.
        dic: Dictionary with the graph.
    """

    graph = filePath.split('/')[1:]

    # Something inside the graph.
    if (len(graph) == 2): 
        if (graph[0] in dic):
            # Wants all information about that vertex.
            if (graph[1] in dic[graph[0]]['vertices']):
                sendInfoEdge(conn, graph[1], dic[graph[0]])

                return True
                

            # Wants only the weight.
            elif (graph[1] in dic[graph[0]]['pesos']):
                message = dic[graph[0]]['pesos'][graph[1]]

                conn.sendall(HTTP200.encode())
                conn.sendall(json.dumps(message).encode())

                return True
            
            else:
                conn.sendall(HTTP404.encode())

                return False

    
    # The client wants the hole graph.
    else:
        if(graph[0] in dic):
            conn.sendall(HTTP200.encode())
            conn.sendall(json.dumps(dic[graph[0]]).encode())

            return True

        else:
            conn.sendall(HTTP404.encode())

            return False

def GETRequest(conn, filePath, dic):
    """
    Send a response to a GET request.
    
    Args:
        conn: Socket connection.
        filePath: The file requested.
        dic: Dictionary with the graph.
    """
    # Is the client trying to access something not allowed?
    if (filePath.find('..') != -1):
        conn.sendall(HTTP400.encode())
        return

    
    if(sendGraph(conn, filePath, dic)):
        return


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
    Send a response to a POST request. Create the resource.

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
    edge = resource[-1].find('-')
   
    # Insert an empty edge or with weigth in a graph that
    # already exists.
    if ((graph in dic) and ((values != 'NULL') or (edge != -1))):
        values = values.split('=')
        values[0] = resource[-1]

        if (len(values) == 2):
            if (values[0] not in dic[graph]['pesos'] or dic[graph]['pesos'][values[0]] == ""):
                create = True
                dic[graph]['pesos'][values[0]] = values[1]

        elif (edge not in dic[graph]['pesos']):
            create = True 
            dic[graph]['pesos'][values[0]] = ""

        else:
            conn.sendall(HTTP400.encode())
            return
   
    # Creat an empty graph of with one vertex.
    else:
        if (edge == -1):
            if(graph not in dic):
                dic[graph] = {}
                dic[graph]['vertices'] = []
                dic[graph]['pesos'] = {}
                create = True
        
            for edge in resource[1:]:
                if (edge not in dic[graph]['vertices']):
                    create = True
                    dic[graph]['vertices'].append(edge)

    if (create):
        conn.sendall(HTTP201.encode())

    else:
        conn.sendall(HTTP400.encode())

def PUTRequest(conn, resource, values, dic):
    """
    Send a response to a PUT request. Edit the resource.

    Args:
       conn: Socket connection. 
       resource: What the client is trying to reach.
       values: The value that the client wants to insert.
       dic: A dictionary with resorces and values.
    """
    create = True 
    resource = resource.split('/')
    resource = resource[1:]
    graph = resource[0]

    if ((values != 'NULL')):
        values = values.split('=')
        values[0] = resource[-1]

        if (len(values) == 2):
            if (values[0] in dic[graph]['pesos'] or dic[graph]['pesos'][values[0]] == ""):
                create = False
                dic[graph]['pesos'][values[0]] = values[1]

        else:
            conn.sendall(HTTP400.encode())
            return
    
    if (not create):
        conn.sendall(HTTP200.encode())

    else:
        conn.sendall(HTTP400.encode())

def removeAllOccurence(graph, vertex, dic):
    """
    Remove all occurence of an vertex form the dictionary.

    Args:
       graph: Graph that is going to be removed.
       vertex: Edge that is going to be removed.
       dic: Where is the information to be removed.
    """
    for key in list(dic[graph]['pesos'].keys()):
        if (vertex in key):
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

    if(len(resource) == 2):
        # Remove the vertex and all its weigth.
        if(resource[1] in dic[graph]['vertices']):
            index = dic[graph]['vertices'].index(resource[1])
            del(dic[graph]['vertices'][index])
            removeAllOccurence(graph, resource[1], dic)
            conn.sendall(HTTP200.encode())

            return 

        # Remove just the weigth.
        if (resource[1] in dic[graph]['pesos']):
            del(dic[graph]['pesos'][resource[1]])
            conn.sendall(HTTP200.encode())

            return 

        else:
            conn.sendall(HTTP204.encode())


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
    sockets = []

    print("Starting server on: " + str(PORT) + ".")
    
    # Create a inet, and streaming socket. 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Tells the kernel to reuse the socket.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)

    sockets.append(sock)


    while True:
        try:
            inputR, outputR, exceptR = select.select(sockets, [], [])
        except select.error as err:
            print("Something happened! Error: ", err) 

        for newSock in sockets:
            try:
                if newSock == sock:
                    conn, addr = sock.accept()
                    sockets.append(conn)

                else:

                    client = (newSock.recv(BUFFER)).decode('utf-8')

                    # Doing this we have an array with the requisitation.
                    # [0] => HTTP Method.
                    # [1] => File requisitation.
                    # [2] => HTTP version.
                    # ...
                    fullrequest = client.split('\r\n')
                    fullrequest = list(filter(None, fullrequest))
                    fullrequest = fullrequest[0].split(' ') + fullrequest[1:]

                    if (fullrequest[0] == 'GET'):
                        GETRequest(newSock, CUR_DIR + fullrequest[1], dic)

                    elif (fullrequest[0] == 'POST'):
                        POSTRequest(newSock, fullrequest[1], fullrequest[-1], dic)

                    elif (fullrequest[0] == 'PUT'):
                        PUTRequest(newSock, fullrequest[1], fullrequest[-1], dic)

                    elif (fullrequest[0] == 'DELETE'):
                        DELETERequest(newSock, fullrequest[1], dic)

                    newSock.close()
                    sockets.remove(newSock)

            except socket.error as err:
                print("Something happened! Error: ", err)

if __name__ == "__main__":
    main()


