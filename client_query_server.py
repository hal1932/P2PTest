# encoding: utf-8
import utils
import protocols
import log
import http
import config
import  hostinfo

import functools
import urllib
import json
import SimpleHTTPServer


class _ClientQueryRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()


class ClientQueryRequestServer(http.ServerBase):

    def __init__(self, query_port):
        self.__query_port = query_port
        super(ClientQueryRequestServer, self).__init__(
            '', query_port,
            _ClientQueryRequestHandler,
        )

    def create_notification(self):
        return protocols.notify_address(self.__query_port)
