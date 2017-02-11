# encoding: utf-8
import log
import config

import SimpleHTTPServer

import http


class _ContentRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.end_headers()
            return

        log.write(self.path)


class ContentServer(http.ServerBase):

    def __init__(self, port=config.PEER_CONTENT_PORT_BASE):
        super(ContentServer, self).__init__('', port, _ContentRequestHandler)
