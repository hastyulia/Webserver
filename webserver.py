import os
import sys
import socket
from threading import Thread
from datetime import datetime as date
from proxy_pass import replacement_proxy_pass


OK_RESPONSE = ' 200 OK\r\n'
CREATE_RESPONSE = ' 201 Created\r\n'
NOT_FOUND_RESPONSE = ' 404 Not Found\r\n'
NO_CONTENT_RESPONSE = ' 204 No Content\r\n'
METHOD_NOT_ALLOWED = ' 405 Method Not Allowed\r\n'
FOLDER = '/Users/hastyulia/Documents/GitHub/Python_tasks/'
ALLOW_METHODS = 'Allow: OPTIONS, GET, HEAD, POST, PUT, DELETE\r\n'
HEADS = ('Content-Type: text/html; charset=UTF-8\r\n'
         'Transfer-Encoding: chunked\r\n')


class WebServer(Thread):
    def __init__(self, client_connection: socket.socket) -> None:
        super().__init__()
        self.client_connection = client_connection

    def run(self) -> None:
        request = b''
        while True:
            body = self.client_connection.recv(2048)
            request += body
            if body.find(b'\r\n\r\n'):
                break

        self.http_request_parse(request)
        self.client_connection.shutdown(1)
        self.client_connection.close()

    def http_request_parse(self, request: bytes) -> None:
        request = request.decode()
        proxy = replacement_proxy_pass(request, self.client_connection)
        if proxy:
            return
        connection_keep_alive = request.find('Connection: keep-alive')
        if connection_keep_alive != -1:
            self.process_request(request, 'Connection: keep-alive')
            request = b''
            while True:
                try:
                    body = self.client_connection.recv(2048)
                    request += body
                    if body.find(b'\r\n\r\n'):
                        request = request.decode()
                        self.process_request(request, 'Connection: keep-alive')
                except socket.timeout:
                    break

        else:
            self.process_request(request, 'Connection: close')

    def process_request(self, request: str, keep_alive: str) -> None:
        method = request.split()[0]
        if method == 'GET':
            self.do_get(request, keep_alive)

        elif method == 'HEAD':
            self.do_head(request, keep_alive)

        elif method == 'POST':
            self.do_insert(request, 'a', keep_alive)

        elif method == 'DELETE':
            self.do_delete(request, keep_alive)

        elif method == 'PUT':
            self.do_insert(request, 'w', keep_alive)

        elif method == 'OPTIONS':
            self.do_options(request, keep_alive)

        else:
            response = (request.split()[2] + METHOD_NOT_ALLOWED
                        + date.strftime(date.now(), '%a, %d %b %Y %H:%M:%S ')
                        + 'GMT\r\n' + HEADS + '\r\n\r\n').encode()
            self.client_connection.sendall(response)

    def do_get(self, request: str, keep_alive: str) -> None:
        split_request = request.split()
        path = os.path.join(FOLDER, split_request[1])
        http_version = split_request[2]
        try:
            with open(path, 'r') as file:
                response = (http_version + OK_RESPONSE + date.strftime(
                            date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                            + HEADS + keep_alive + '\r\n\r\n').encode()
                self.client_connection.sendall(response)
                self.client_connection.sendall(file.read().encode())

        except IOError:
            response = (http_version + NOT_FOUND_RESPONSE + date.strftime(
                        date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                        + HEADS + keep_alive + '\r\n\r\n').encode()
            self.client_connection.sendall(response)

    def do_head(self, request: str, keep_alive: str) -> None:
        split_request = request.split()
        path = os.path.join(split_request[1])
        http_version = split_request[2]
        try:
            with open(path) as _:
                response = (http_version + OK_RESPONSE + date.strftime(
                            date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                            + HEADS + keep_alive + '\r\n\r\n').encode()

        except IOError:
            response = (http_version + NOT_FOUND_RESPONSE + date.strftime(
                        date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                        + HEADS + keep_alive + '\r\n\r\n').encode()
        self.client_connection.sendall(response)

    def do_insert(self, request: str, mode: str, keep_alive: str) -> None:
        while True:
            body = self.client_connection.recv(2048)
            request += body.decode()
            if body.find(b'\r\n\r\n'):
                break
        split_request = request.split('\r\n\r\n')
        head = split_request[0]
        body = split_request[1]
        path = os.path.join(head.split()[1])
        http_version = head.split()[2]
        location = f'Content-Location: {path}\r\n'
        try:
            with open(path, mode) as file:
                file.read(1)
                file.write(body)
                response = (http_version + OK_RESPONSE + date.strftime(
                            date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                            + HEADS + keep_alive + location
                            + '\r\n\r\n').encode()

        except IOError:
            with open(path, 'w') as file:
                file.write(body)
                response = (http_version + CREATE_RESPONSE + date.strftime
                            (date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                            + HEADS + keep_alive + location
                            + '\r\n\r\n').encode()
        self.client_connection.sendall(response)

    def do_delete(self, request: str, keep_alive: str) -> None:
        split_request = request.split()
        path = os.path.join(split_request[1])
        http_version = split_request[2]
        try:
            os.remove(path)
            response = (http_version + NO_CONTENT_RESPONSE + date.strftime
                        (date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                        + HEADS + keep_alive + '\r\n\r\n').encode()

        except IOError:
            response = (http_version + NOT_FOUND_RESPONSE + date.strftime
                        (date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n'
                        + HEADS + keep_alive + '\r\n\r\n').encode()
        self.client_connection.sendall(response)

    def do_options(self, request: str, keep_alive: str) -> None:
        split_request = request.split()
        http_version = split_request[2]
        response = (http_version + OK_RESPONSE + ALLOW_METHODS + date.strftime(
                    date.now(), '%a, %d %b %Y %H:%M:%S ') + 'GMT\r\n' + HEADS
                    + keep_alive + '\r\n\r\n').encode()
        self.client_connection.sendall(response)


def listen(host='127.0.0.1', port=17000) -> None:
    browser_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    browser_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    browser_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    browser_connection.bind((host, port))
    browser_connection.listen(20)
    while True:
        current_connection, address = browser_connection.accept()
        server = WebServer(current_connection)
        server.start()


if __name__ == '__main__':
    proxy_host = input('Enter proxy host: ')
    proxy_port = int(input('Enter proxy port: '))
    try:

        listen(proxy_host, proxy_port)
    except KeyboardInterrupt:
        sys.exit()
