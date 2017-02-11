# encoding: utf-8
import config
import protocols
import http
import log
import utils
import client_info

import pycurl

import functools
import urllib
import threading
import time


class ClientPool(object):

    def __init__(self):
        self.__clients = []
        self.__clients_lock = threading.Lock()

        def _on_client_disconnected(client):
            with self.__clients_lock:
                log.write('client is disconnected: {}'.format(client.host))
                self.__clients.remove(client)

        self.__client_watcher_thread = _ClientWatcherThread(self.__clients, _on_client_disconnected)

    @property
    def clients(self):
        return self.__clients

    def start_accepting_clients(self):
        utils.create_nsq_reader(
            config.TOPIC_REGISTER_CLIENT,
            functools.partial(ClientPool.__on_register_client, instance=self)
        )

        self.__client_watcher_thread.start()

    def stop_accepting_clients(self):
        raise NotImplementedError()

    @staticmethod
    def __on_register_client(message, instance):
        data = protocols.deserialize_nsq_message(message)
        instance.__process_registration(data)

    def __process_registration(self, data):
        # log.write(data)

        operation = data['ope']
        user = data['user']
        host = data['host']
        arguments = data['args']

        error = None

        if error is None and operation != 'register':
            error = 'invalid registration request: {}'.format(data)

        if error is None:
            requisite_args = [
                'notification_port',
                'content_port',
            ]
            for requisite_arg in requisite_args:
                if requisite_arg not in arguments:
                    error = 'invalid registration arguments: {}'.format(arguments)
                    break

        if error is None:
            notification_port = arguments['notification_port']
            content_port = arguments['content_port']
            error = self.__register_client(host, user, notification_port, content_port)

        if error is not None:
            log.warning('registration error: {}'.format(error))
            if 'notification_port' in arguments:
                notification_port = arguments['notification_port']
                self.__register_client_complete(host, notification_port, error)
            return

        log.write('accept client: {}, {}:{}'.format(user, host, content_port))

    def __register_client(self, host, user, notification_port, content_port):
        with self.__clients_lock:
            error = self.__test_register_client(host, user)
            if error is not None:
                return error

            if not self.__register_client_complete(host, notification_port):
                return 'client not found: {}:{}'.format(host, notification_port)

        self.__clients.append(client_info.ClientInfo(host, user, content_port))

        return None

    def __register_client_complete(self, host, notification_port, error=None):
        if error is None:
            result = http.RESULT_SUCCESS
        else:
            result = urllib.quote(error)

        code, _ = http.get_sync(
            'http://{}:{}?result={}'.format(host, notification_port, result))
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
                code = 0
                timeout = False
                try:
                    code, _ = http.get_sync(client.ping_url, self.__timeout)
                except pycurl.error as e:
                    if e.args[0] == pycurl.E_OPERATION_TIMEDOUT:
                        log.warning('ping to the client is timed out: {}'.format(client.ping_url))
                        timeout = True
                    else:
                        raise e

                is_client_alive = not timeout
                if is_client_alive and code == 200:
                    log.write('client is alive: {}'.format(client.ping_url))
                elif not timeout:
                    log.warning('client may be dead: {}, {}'.format(code, client.ping_url))
                    is_client_alive = False

                if not is_client_alive:
                    disconnected_clients.append(client)

            if len(disconnected_clients) > 0:
                for client in disconnected_clients:
                    self.__on_client_disconnected(client)

            time.sleep(self.__polling_interval)
            # time.sleep(1)

    def stop(self):
        self.__stop_event.set()
        self.join()





