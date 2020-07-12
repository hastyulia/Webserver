import socket
import unittest
import webserver
from unittest import mock


class WebServerTests(unittest.TestCase):
    def test_listen(self) -> None:
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = ''
        with mock.patch('socket.socket') as mock_socket:
            mock_socket.return_value.accept.return_value = ('', -1)
            with mock.patch('webserver.WebServer') as mock_server:
                mock_server.return_value = 'ggg'
                with self.assertRaises(AttributeError):
                    webserver.listen()

    def test_server_init(self) -> None:
        mock_socket = mock.Mock()
        server = webserver.WebServer(mock_socket)
        self.assertEqual(server.client_connection, mock_socket)

    def test_server_run(self) -> None:
        mock_socket = mock.Mock()
        with mock.patch('socket.socket') as mock_sendall:
            mock_sendall.return_value.recv.return_value = b''
            mock_socket.recv.return_value = b'GET /zxc HTTP/1.1\r\n\r\n'
            server = webserver.WebServer(mock_socket)
            self.assertEqual(server.run(), None)

    def test_server_get(self) -> None:
        request = b'GET /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with mock.patch('socket.socket') as mock_sendall:
            mock_sendall.return_value.recv.return_value = b''
            with self.assertRaises(OSError):
                server.http_request_parse(request)

    def test_server_get1(self) -> None:
        request = b'GET aaa/index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            with mock.patch('builtins.open',
                            mock.mock_open(read_data='data')) as _:
                server.http_request_parse(request)

    def test_server_put(self) -> None:
        request = b'PUT /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            server.http_request_parse(request)

    def test_server_insert_put(self) -> None:
        request = 'PUT /index.py HTTP/1.1\r\n'
        connection = mock.Mock()
        connection.recv.return_value = b'a b c\r\nd f\r\n\r\n'
        server = webserver.WebServer(connection)
        with mock.patch('builtins.open',
                        mock.mock_open(read_data='data')) as _:
            self.assertEqual(server.do_insert(request, 'w',
                                              'Connection: close'), None)

    def test_server_delete(self) -> None:
        request = b'DELETE /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            server.http_request_parse(request)

    def test_server_delete1(self) -> None:
        request = b'DELETE /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            with mock.patch('os.remove') as _:
                server.http_request_parse(request)

    def test_server_head(self) -> None:
        request = b'HEAD /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            server.http_request_parse(request)

    def test_server_head1(self) -> None:
        request = b'HEAD aaa/index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            with mock.patch('builtins.open',
                            mock.mock_open(read_data='data')) as _:
                server.http_request_parse(request)

    def test_server_options(self) -> None:
        request = b'OPTIONS /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            server.http_request_parse(request)

    def test_server_options1(self) -> None:
        request = b'OPTIONS aaa/index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            with mock.patch('builtins.open',
                            mock.mock_open(read_data='data')) as _:
                server.http_request_parse(request)

    def test_server_post(self) -> None:
        request = b'POST /index.py HTTP/1.1\r\n'
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server = webserver.WebServer(connection)
        with self.assertRaises(OSError):
            server.http_request_parse(request)

    def test_server_insert_post(self) -> None:
        request = 'POST /index.py HTTP/1.1\r\n'
        connection = mock.Mock()
        connection.recv.return_value = b'a b c\r\nd f\r\n\r\n'
        server = webserver.WebServer(connection)
        with mock.patch('builtins.open',
                        mock.mock_open(read_data='data')) as _:
            self.assertEqual(server.do_insert(request, 'a',
                                              'Connection: close'), None)

    def test_server_insert_does_not_exist(self) -> None:
        request = 'POST /index.py HTTP/1.1\r\n'
        connection = mock.Mock()
        connection.recv.return_value = b'a b c\r\nd f\r\n\r\n'
        connection.sendall.side_effect = IOError
        server = webserver.WebServer(connection)
        with mock.patch('builtins.open',
                        mock.mock_open(read_data='data')) as _:
            with self.assertRaises(IOError):
                self.assertEqual(server.do_insert(request, 'a',
                                                  'Connection: close'), None)
