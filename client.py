#!/usr/bin/python

"""
Authors:
    Augusto Melo.
    Danilo Ikeda.
    Gustavo Silva.
"""

import sys
import socket

REQUEST = "GET "
PROTOCOL = "HTTP/1.1.\nHost: "
PORT = 80

BUFFER = 10000

def makeRequisition(url):
    """
    Make the request that will be send to the server.

    Args:
        url: Url typed by the user.

    Return:
        request: A dictionarie following the pattern;
            [0] => request.
            [1] => location.
            [2] => protocol.
            [3] => host.
            [4] => \n\n.
            [5] => port.
    """
    request = []

    request.append(REQUEST)

    #Look for the location request.
    indGet = sys.argv[1].find('/')
   
    # Does the requet has a place?
    if (indGet != -1):
        # Location.
        request.append(sys.argv[1][indGet:] + ' ')
        request.append(PROTOCOL)
        # Host
        request.append(sys.argv[1][:indGet])

    else:
        # No, append root to the request.
        indGet = len(sys.argv[1])
        # Location.
        request.append('/ ')
        request.append(PROTOCOL)
        # Host.
        request.append(sys.argv[1])

    # Append the \n\n
    request.append('\n\n')
    # Port.
    request.append(None)

    #Look for a localhost request.
    indLH = sys.argv[1].find(':')
    
    if (indLH != -1):
        # Update host.
        request[3] = sys.argv[1][:indLH]
        # Update port.
        request[-1] = int(sys.argv[1][(indLH+1):indGet])

    return request


def main():
    # Verify the number of arguments.
    if(len(sys.argv) == 1):
        print("You have to pass a site as an argument.")
        return 1

    # Create a inet, and sterming socket.   
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Create request.
    req = makeRequisition(sys.argv[1])

    # The port was set?
    if(req[-1] is None):
        # No, use the default port.
        port = PORT

    else:
        port = req[-1]
    
    request = ''.join(req[:-1])

    request = request + "\n\n"

    sock.connect((req[3], port))
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
