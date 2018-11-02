import tcpbee.handlers
import firenado.tornadoweb


class TcpbeeComponent(firenado.tornadoweb.TornadoComponent):

    def get_handlers(self):
        return [
            (r'/.*', tcpbee.handlers.IndexHandler),
        ]
