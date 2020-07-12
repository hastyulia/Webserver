import unittest
from unittest import mock
from proxy_pass import replacement_proxy_pass


class ReplacementTests(unittest.TestCase):
    def test_replacement(self) -> None:
        request = 'GET /qwe/index.py HTTP/1.1\r\n'
        mock_sock = mock.Mock()
        mock_sock.recv.return_value = ''
        with mock.patch('socket.socket') as mock_sendall:
            mock_sendall.return_value.recv.return_value = b''
            self.assertEqual(replacement_proxy_pass(request, mock_sock), True)
