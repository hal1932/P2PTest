# encoding: utf-8
import config

import requests
import requests.exceptions
import grequests

import SocketServer
import threading
import SimpleHTTPServer
import time
import urlparse


RESULT_SUCCESS = 'OK'
NSQ_HTTP_PUB_RESULT_SUCCESS = 'OK'


RequestError = requests.exceptions.RequestException


def get_sync(url, timeout=None):
    kwargs = {}
    if time is not None:
        kwargs['timeout'] = (timeout, timeout)
    response = requests.get(url, **kwargs)
    return response.status_code, response.text


def get_all_sync(urls, timeout=None):
    kwargs = {}
    if time is not None:
        kwargs['timeout'] = (timeout, timeout)

    request_set = (grequests.get(url, timeout=(timeout, timeout)) for url in urls)

    tmp = {'errors': {}}

    def _exception_handler(request, exception):
        tmp['errors'][request.url] = exception

    response_set = grequests.map(request_set, exception_handler=_exception_handler)

    result = {}
    for response in response_set:
        if response is not None:
            result[response.url] = (response.status_code, response.content)

    for url, exception in tmp['errors'].items():
        result[url] = (0, exception)

    return result


def post_sync(url, data, timeout=None):
    kwargs = {}
    if time is not None:
        kwargs['timeout'] = (timeout, timeout)
    response = requests.post(url, data, **kwargs)
    return response.status_code, response.text


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
