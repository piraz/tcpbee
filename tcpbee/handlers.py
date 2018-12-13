from firenado import tornadoweb
import sys
import tornado.httpclient
from tornado import gen
from tornado.httputil import HTTPHeaders
import traceback
import collections
from xml.dom import minidom

cache = {}

cache_length = {}


class IndexHandler(tornadoweb.TornadoHandler):

    #def compute_etag(self):
        # disable tornado Etag
        #return None

    @gen.coroutine
    def get(self):
        self.request.body = None
        yield self.post()

    @gen.coroutine
    def post(self):
        yield self.forward(80, "localhost")

    def handle_response(self, response):
        if response.error and not isinstance(response.error,
                                             tornado.httpclient.HTTPError):
            print("response has error %s" % response.error)

            self.set_status(500)
            self.write("Internal server error:\n" + str(response.error))
            self.finish()
        else:
            self.set_status(response.code, response.reason)
            # clear tornado default header
            self.clear()
            print(response.code)
            #print(response.getSize())
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            print(response.headers)
            for header, v in response.headers.get_all():
                if header not in ("Content-Length", "Transfer-Encoding",
                                  "Content-Encoding", "Connection",
                                  "Last-Modified"):
                    # Remove Last-Modified because of
                    # https://github.com/tornadoweb/tornado/issues/2262
                    # some header appear multiple times, eg 'Set-Cookie'
                    self.set_header(header, v)
            #xml = minidom.parseString(response.body.decode())
            #self._headers
            #print(xml.toprettyxml())
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            if response.body:
                content_lenght = len(response.body)
                self.set_header('Content-Length', content_lenght)
                self.write(response.body)
            try:
                if response.code == 200:
                    self.finish()
            except RuntimeError:
                pass

    @gen.coroutine
    def forward(self, port=None, host=None):
        try:
            tornado.httpclient.AsyncHTTPClient.configure(
                'tcpbee.socket_curl_httpclient.UnixSocketCurlAsyncHTTPClient',
                **{"unix_socket_path": "/tmp/djdjdjddjdj"}
            )
            client = tornado.httpclient.AsyncHTTPClient()

            headers = HTTPHeaders()
            # Overriding cache, forcing no cache
            for header in self.request.headers:
                if header not in ["If-None-Match", "Host"]:
                    if header == "Cache-Control":
                        headers.add(header, "no-cache")
                        headers.add("Pragma", "no-cache")
                    else:
                        headers.add(header, self.request.headers.get(header))
            print(self.request.headers)
            print("------------------------------------------------")
            print(headers)
            yield client.fetch(
                tornado.httpclient.HTTPRequest(
                    url="%s%s" % (
                        "http://localhost", self.request.uri),
                    method=self.request.method,
                    body=self.request.body,
                    headers=headers),
                self.handle_response)
        except tornado.httpclient.HTTPError as x:
            print("tornado signalled HTTPError %s" % x)
            if x.code == 304:
                self.code = 304
            else:
                if hasattr(x, "response") and x.response:
                    yield self.handle_response(x.response)
            try:
                self.finish()
            except RuntimeError:
                pass
        except tornado.httpclient.CurlError as x:
            print("tornado signalled CurlError %s" % x)
            self.set_status(500)
            self.write("Internal server error:\n" + "".join(
                traceback.format_exception(*sys.exc_info())))
            self.finish()
        except:
            self.set_status(500)
            self.write("Internal server error:\n" + ''.join(
                traceback.format_exception(*sys.exc_info())))
            self.finish()
