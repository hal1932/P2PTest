# encoding: utf-8
import config

import pycurl

import StringIO
import SocketServer
import threading
import SimpleHTTPServer
import time
import urlparse


RESULT_SUCCESS = 'OK'
NSQ_HTTP_PUB_RESULT_SUCCESS = 'OK'


def get_sync(url, timeout=None):
    response = StringIO.StringIO()

    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, response)
    if timeout is not None:
        curl.setopt(pycurl.TIMEOUT, timeout)
    curl.perform()

    code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()

    return code, response.getvalue()


def post_sync(url, data, timeout=None):
    response = StringIO.StringIO()

    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.POSTFIELDS, data)
    curl.setopt(pycurl.WRITEDATA, response)
    if timeout is not None:
        curl.setopt(pycurl.TIMEOUT, timeout)
    curl.perform()

    code = curl.getinfo(pycurl.RESPONSE_CODE)
    curl.close()

    return code, response.getvalue()


def nsq_pub_sync(topic, data, timeout=None):
    url = 'http://{}/pub?topic={}'.format(config.NSQD_HTTP_ADDRESS, topic)
    return post_sync(url, data, timeout)


class ServerBase(object):

    def __init__(self, host, port, handler):
        server = SocketServer.ThreadingTCPServer((host, port), handler)
        serve_thread = threading.Thread(target=server.serve_forever)
        serve_thread.daemon = True

        self.__server = server
        self.__serve_thread = serve_thread

    def start(self):
        self.__serve_thread.start()
        return self

    def stop(self):
        self.__server.shutdown()
        self.__server.server_close()
        self.__serve_thread.join()


class _CommonRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    on_get_request = None

    def do_GET(self):
        if _CommonRequestHandler.on_get_request is not None:
            _CommonRequestHandler.on_get_request(self)


class _CommonServer(ServerBase):

    def __init__(self, port, on_get_request=None):
        _CommonRequestHandler.on_get_request = on_get_request
        super(_CommonServer, self).__init__('', port, _CommonRequestHandler)


def wait_for_get_request(port, predicate, polling_interval=1):
    tmp = {'queries': None, 'predicate': predicate}

    def _on_get(handler):
        _params = urlparse.urlparse(handler.path)
        _queries = urlparse.parse_qs(_params.query)
        if tmp['predicate'](_queries):
            tmp['queries'] = _queries

        handler.send_response(200)
        handler.end_headers()

    server = _CommonServer(port, on_get_request=_on_get)
    server.start()

    while tmp['queries'] is None:
        time.sleep(polling_interval)

    server.stop()

    return tmp['queries']
