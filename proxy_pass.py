import re
import socket


PROXY_FILENAME = 'proxy_pass.txt'
BUFFER_SIZE = 1024


def replacement_proxy_pass(request: str,
                           client_connection: socket.socket) -> bool:
    proxy = False
    split_request = request.split(' ')
    path = split_request[1].split('/')[1]
    with open(PROXY_FILENAME) as file:
        for line in file:
            if path in line:
                proxy = True
                request = re.sub(r'/[a-zA-Z]*\d*', line.split()[4], request, 1)
    if proxy:
        server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server_connection.sendall(request.encode())
        response = b''
        while True:
            data = server_connection.recv(BUFFER_SIZE)
            response += data
            if not data:
                break
        client_connection.sendall(response)

    return proxy
