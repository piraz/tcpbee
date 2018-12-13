import pycurl  # type: ignore
from tornado.curl_httpclient import CurlAsyncHTTPClient


def opensocket(_, __, curl_address):
    import socket
    family, socktype, protocol, address = curl_address
    s = socket.socket(family, socktype, protocol)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    return s


# Following examples from
# https://github.com/pycurl/pycurl/blob/master/tests/open_socket_cb_test.py
class UnixSocketCurlAsyncHTTPClient(CurlAsyncHTTPClient):

    def initialize(self, unix_socket_path=None, max_clients=10, defaults=None):
        self.unix_socket_path = unix_socket_path
        super(UnixSocketCurlAsyncHTTPClient, self).initialize(
            max_clients=10, defaults=defaults
        )

    def _curl_create(self):
        curl = super(UnixSocketCurlAsyncHTTPClient, self)._curl_create()
        curl.setopt(pycurl.UNIX_SOCKET_PATH, self.unix_socket_path)
        curl.setopt(pycurl.OPENSOCKETFUNCTION,
                    lambda purpose, address: opensocket(
                        curl, purpose, address
                    ))
        return curl
