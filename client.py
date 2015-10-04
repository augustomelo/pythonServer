#!/usr/bin/python

"""
Authors:
    Augusto Melo.
    Danilo Ikeda.
    Gustavo Silva.
"""

import sys
import socket

GET = "GET "
PROTOCOL = "HTTP/1.1.\r\nHost: "
C_TYPE = "\r\nContent-Type: application/x-www-form-urlencoded\r\n"
C_LENGTH = "Content-Length: "
PORT = 80

BUFFER = 10000

# Example /grafo3
# Example /grafo3/vertice1-vertice2
# Example /grafo3/vertice1-vertice2?peso=10
def makeRequest(url, method):
    """
    Make a request using the method typed by the user.

    Args:
        url: Url typed by the user.
        method: POST, PUT or DELETE method.

    Return:
        request: A vector following the pattern;
            [0] => request.
            [1] => location.
            [2] => protocol.
            [3] => host.
            [4] => content-type.
            [5] => content-length.
            [6] => body
            [7] => \r\n\r\n.
            [8] => port.
    """
    request = []

    request.append(method + ' ')

    qMark = url.find('?')

    indSlash = url.find('/')

    # Does the requet has a place?
    if (indSlash != -1):
        # Location.
        request.append(url[indSlash:qMark] + ' ')
        request.append(PROTOCOL)
        # Host
        request.append(url[:indSlash])

    else:
        # No, append root to the request.
        indSlash = len(url)
        # Location.
        request.append('/ ')
        request.append(PROTOCOL)
        # Host.
        request.append(url)

    # Append the content-type
    request.append(C_TYPE)

    # Append the content-length
    request.append(C_LENGTH + str(len(url[qMark+1:])) + '\r\n\r\n')

    # Append the message
    if(qMark == -1):
        request.append('NULL')

    else:
        request.append(url[qMark+1:])

    # Append the \n\n
    request.append('\r\n\r\n')
    
    # Port.
    request.append(None)

    #Look for a localhost request.
    indLH = url.find(':')
    
    if (indLH != -1):
        # Update host.
        request[3] = url[:indLH]
        # Update port.
        request[-1] = int(url[(indLH+1):indSlash])

    return request



def makeGETRequest(url):
    """
    Make the GET request.

    Args:
        url: Url typed by the user.

    Return:
        request: A vector following the pattern;
            [0] => request.
            [1] => location.
            [2] => protocol.
            [3] => host.
            [4] => \r\n\r\n.
            [5] => port.
    """
    request = []

    request.append(GET)

    #Look for the location request.
    indGet = url.find('/')
   
    # Does the requet has a place?
    if (indGet != -1):
        # Location.
        request.append(url[indGet:] + ' ')
        request.append(PROTOCOL)
        # Host
        request.append(url[:indGet])

    else:
        # No, append root to the request.
        indGet = len(url)
        # Location.
        request.append('/ ')
        request.append(PROTOCOL)
        # Host.
        request.append(url)

    # Append the \n\n
    request.append('\r\n\r\n')
    # Port.
    request.append(None)

    #Look for a localhost request.
    indLH = url.find(':')
    
    if (indLH != -1):
        # Update host.
        request[3] = url[:indLH]
        # Update port.
        request[-1] = int(url[(indLH+1):indGet])

    return request

def main():
    # Verify the number of arguments.
    if(len(sys.argv) == 1):
        print("You have to pass a site as an argument.")
        return 1

    # Create a inet, and sterming socket.   
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.settimeout(5)

    # Create request.
    if (len(sys.argv) == 3):
        req = makeRequest(sys.argv[1], sys.argv[2])
    else:
        req = makeGETRequest(sys.argv[1])

    # The port was set?
    if(req[-1] is None):
        # No, use the default port.
        port = PORT

    else:
        port = req[-1]
    
    request = ''.join(req[:-1])


    # VERIFY REQUEST
    print(request)

    try:
        sock.connect((req[3], port))

    except socket.timeout:
        print("It was not possible to connect to '" + req[3] + "' in the given time, verify the host name and try again.\nExiting.") 
        sys.exit(0)

    sock.send(request.encode())
    resp = sock.recv(BUFFER)


    # Output the respose.
    while(len(resp) > 0):
        print(resp.decode('utf-8'))
        resp = sock.recv(BUFFER)

    sock.close()

    return 0


if __name__ == "__main__":
    main()
