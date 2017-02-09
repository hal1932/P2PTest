# encoding: utf-8
import hostinfo

import json


class Protocol(object):
    def __init__(self, data):
        self.host = data['host']
        self.user = data['user']
        self.operation = data['ope']

        self.arguments = None
        if 'args' in data:
            self.arguments = data['args']


def serialize(data):
    return json.dumps(data)


def deserialize(data):
    data = json.loads(data)
    return Protocol(data)


def registration():
    data = __create_container('register')
    return serialize(data)


def __create_container(operation, arguments=None):
    data = {
        'host': hostinfo.get_ipv4_address(),
        'user': hostinfo.get_user(),
        'ope': operation
    }

    if arguments is not None:
        data['args'] = arguments

    return data

