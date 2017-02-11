# encoding: utf-8
from __future__ import print_function

import config
import protocols

import nsq
import tornado.gen

import sys
import functools
import json
import time


def main(args):
    clients = []
    nsq.Reader(
        topic='p2ptest_clients',
        channel='test',
        message_handler=functools.partial(_on_update_client_status, clients),
        nsqd_tcp_addresses=config.NSQD_TCP_ADDRESSES,
    )
    nsq.run()


def _on_update_client_status(message, clients):
    message.enable_async()
    data = protocols.deserialize(message.body)
    message.finish()

    if data.operation == 'register':
        print('register: {}, {}'.format(data.host, data.user))
    else:
        print(data)


if __name__ == '__main__':
    main(sys.argv)
