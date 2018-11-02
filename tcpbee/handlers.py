from firenado import tornadoweb
import tornado.httpclient
from tornado import gen
import sys
import traceback
from xml.dom import minidom


class IndexHandler(tornadoweb.TornadoHandler):

    def compute_etag(self):
        # disable tornado Etag
        return None

    @gen.coroutine
    def get(self):
        yield self.forward(7000, "localhost")

    @gen.coroutine
    def post(self):
        yield self.get()

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
                                  "Content-Encoding", 'Connection'):
                    # some header appear multiple times, eg 'Set-Cookie'
                    self.add_header(header, v)
            xml = minidom.parseString(response.body.decode())
            self._headers
            print(xml.toprettyxml())
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            if response.body:
                self.set_header('Content-Length', len(response.body))
                self.write(response.body)
            self.finish()

    @gen.coroutine
    def forward(self, port=None, host=None):
        try:
            tornado.httpclient.AsyncHTTPClient.configure(
                'tornado.curl_httpclient.CurlAsyncHTTPClient')
            client = tornado.httpclient.AsyncHTTPClient()
            yield client.fetch(
                tornado.httpclient.HTTPRequest(
                    url="%s://%s:%s%s" % (
                        self.request.protocol, host or "127.0.0.1",
                        port or 80, self.request.uri),
                    method=self.request.method,
                    body=self.request.body,
                    headers=self.request.headers),
                self.handle_response)
        except tornado.httpclient.HTTPError as x:
            print("tornado signalled HTTPError %s" % x)
            if hasattr(x, "response") and x.response:
                yield self.handle_response(x.response)
            self.finish()
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

#https://github.com/senko/tornado-proxy/blob/master/tornado_proxy/proxy.py

#https://medium.com/@DJetelina/python-and-chunked-transfer-encoding-11325245a532
# from http://pycurl.io/docs/latest/install.html#install
# export PYCURL_SSL_LIBRARY=[openssl|gnutls|nss]
