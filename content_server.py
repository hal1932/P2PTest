# encoding: utf-8
import log
import http

import SimpleHTTPServer

import os


class _ContentRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.end_headers()
            return

        content_root = self.server.parameters['content_root']
        content_path = os.path.join(content_root, self.path.lstrip('/'))
        log.write(content_path)
        if not os.path.isfile(content_path):
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-Type', 'application/octet-stream')
        with open(content_path, 'rb') as f:
            self.wfile.write(f.read())
        self.end_headers()


class ContentServer(http.ServerBase):

    def __init__(self, port, content_root):
        super(ContentServer, self).__init__(
            '', port,
            _ContentRequestHandler,
            {'content_root': content_root})
