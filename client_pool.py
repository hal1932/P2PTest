# encoding: utf-8
import config
import protocols
import http
import log
import utils

import pycurl

import functools
import urllib
import threading
import time


class ClientInfo(object):

    def __init__(self, host, user):
        self.__host = host
        self.__user = user

    @property
    def host(self): return self.__host

    @property
    def user(self): return self.__user


class ClientPool(object):

    def __init__(self):
        self.__clients = []
        self.__clients_lock = threading.Lock()

        def _on_client_disconnected(client):
            with self.__clients_lock:
                log.write('client is disconnected: {}'.format(client.host))
                self.__clients.remove(client)

        self.__client_watcher_thread = _ClientWatcherThread(self.__clients, _on_client_disconnected)

    def start_accepting_clients(self):
        utils.create_nsq_reader(
            'p2ptest_register_client',
            functools.partial(ClientPool.__on_register_client, instance=self)
        )

        self.__client_watcher_thread.start()

    def stop_accepting_clients(self):
        pass

    @staticmethod
    def __on_register_client(message, instance):
        message.enable_async()
        data = protocols.deserialize(message.body)
        message.finish()

        log.write(data)

        error = None

        if error is None and data.operation != 'register':
            error = 'invalid registration request: {}'.format(data)

        if error is None and 'notification_port' not in data.arguments:
            error = 'invalid registration arguments: {}'.format(data.arguments)

        if error is None:
            notification_port = data.arguments['notification_port']
            error = instance.__register_client(data.host, data.user, notification_port)

        if error is not None:
            log.warning('registration error: {}'.format(error))
            instance.__register_client_complete(data.host, notification_port, error)
            return

        log.write('accept client: {} {}'.format(data.host, data.user))

    def __register_client(self, host, user, notification_port):
        with self.__clients_lock:
            error = self.__test_register_client(host, user)
            if error is not None:
                return error

            if not self.__register_client_complete(host, notification_port):
                return 'client is disconnected: {}:{}'.format(host, notification_port)

            self.__clients.append(ClientInfo(host, user))

        return None

    def __register_client_complete(self, host, notification_port, error=None):
        if error is None:
            result = 'OK'
        else:
            result = urllib.quote(error)

        code, _ = http.get_sync('http://{}:{}?result={}'.format(host, notification_port, result))
        return code == 200

    def __test_register_client(self, host, user):
        if len(self.__clients) >= config.MAX_CLIENTS_COUNT:
            return 'exceeding the acceptable number of clients'

        def _test_is_same_client(_client, _host, _user):
            if _client.user == _user:
                return 'duplicated client user name: {}, {}'.format(host, user)
            return None

        for client in self.__clients:
            error = _test_is_same_client(client, host, user)
            if error is not None:
                return error

        return None


class _ClientWatcherThread(threading.Thread):

    def __init__(self, clients, on_client_disconnected, timeout=1, polling_interval=60):
        self.__clients = clients
        self.__timeout = timeout
        self.__polling_interval = polling_interval
        self.__stop_event = threading.Event()
        self.__on_client_disconnected = on_client_disconnected
        super(_ClientWatcherThread, self).__init__()
        self.daemon = True

    def run(self):
        while True:
            if self.__stop_event.is_set():
                break

            disconnected_clients = []
            for client in self.__clients:
                url = 'http://{}:{}/ping'.format(client.host, config.PEER_CONTENT_PORT)
                try:
                    code, _ = http.get_sync(url, self.__timeout)
                except pycurl.error as e:
                    if e.args[0] == pycurl.E_OPERATION_TIMEDOUT:
                        disconnected_clients.append(client)
                    else:
                        raise e

                if code == 200:
                    log.write('check if client is alive: {}'.format(client.host))
                else:
                    pass

            if len(disconnected_clients) > 0:
                for client in disconnected_clients:
                    self.__on_client_disconnected(client)

            time.sleep(self.__polling_interval)

    def stop(self):
        self.__stop_event.set()
        self.join()





