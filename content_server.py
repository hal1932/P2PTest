# encoding: utf-8
from __future__ import print_function

import config

import SimpleHTTPServer
import SocketServer
import threading


class _ContentRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        print(self.path)


class _ServeThread(threading.Thread):

    def __init__(self, server):
        super(_ServeThread, self).__init__()
        self.__server = server

    def run(self):
        self.__server.serve_forever()


class ContentServer(object):

    def __init__(self, port):
        server = SocketServer.ThreadingTCPServer(('', port), _ContentRequestHandler)
        serve_thread = threading.Thread(target=server.serve_forever)
        serve_thread.daemon = True

        self.__server = server
        self.__serve_thread = serve_thread

    def start(self):
        self.__serve_thread.start()

    def stop(self):
        self.__server.shutdown()
        self.__server.server_close()
        self.__serve_thread.join()
