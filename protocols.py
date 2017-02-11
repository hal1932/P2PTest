# encoding: utf-8
import hostinfo

import json


def serialize(data):
    return json.dumps(data)


def deserialize(data):
    return json.loads(data)


def deserialize_nsq_message(message):
    message.enable_async()
    data = deserialize(message.body)
    message.finish()
    return data


def registration(notification_port, content_port):
    data = __create_container(
        'register',
        {
            'notification_port': notification_port,
            'content_port': content_port,
        })
    return serialize(data)


def query_clients(query, reply_port):
    data = __create_container(
        'query_clients',
        {
            'query': query,
            'reply_port': reply_port,
        })
    return serialize(data)


def __create_container(operation, arguments=None):
    data = {
        'host': hostinfo.get_ipv4_address(),
        'user': hostinfo.get_user(),
        'ope': operation,
    }

    if arguments is not None:
        data['args'] = arguments

    return data

