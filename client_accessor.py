# encoding: utf-8
import utils
import protocols
import log
import http

import functools
import urllib
import json


class ClientAccessor(object):

    def __init__(self, client_pool):
        self.__client_pool = client_pool

    def start_accepting_query(self):
        utils.create_nsq_reader(
            'p2ptest_query_clients',
            functools.partial(ClientAccessor.__on_received_query, instance=self)
        )

    @staticmethod
    def __on_received_query(message, instance):
        data = protocols.deserialize_nsq_message(message)
        instance.process_query(data)

    def process_query(self, data):
        operation = data['ope']
        host = data['host']
        arguments = data['args']

        log.write(data)

        error = None
        result = None

        if error is None and operation != 'query_clients':
            error = 'invalid query arguments: {}'.format(data)

        if error is None:
            requisite_args = [
                'query',
                'reply_port',
            ]
            for requisite_arg in requisite_args:
                if requisite_arg not in arguments:
                    error = 'invalid registration arguments: {}'.format(arguments)
                    break

        if error is None:
            query = arguments['query']
            result = self.__find_all()

        if error is not None:
            pass
        else:
            reply_port = arguments['reply_port']
            self.__send_result(host, reply_port, result)

    def __find_all(self):
        def _serialize_client(client):
            return {
                'user': client.user,
                'content_url': client.content_url,
            }
        serialized = map(_serialize_client, self.__client_pool.clients)
        return json.dumps(serialized)

    def __send_result(self, host, port, result):
        url = 'http://{}:{}?result={}'.format(host, port, urllib.quote(result))
        code, _ = http.get_sync(url)
        return code == 200


