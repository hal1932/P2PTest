# encoding: utf-8
from __future__ import print_function

import nsq
import tornado.gen

import sys
import functools
import json
import time

NSQD_TCP_ADDRESSES = ['127.0.0.1:4150', ]


def on_update_client_status(message):
    message.enable_async()
    print(message.body)
    message.finish()

    time.sleep(1)


def main(args):
    nsq.Reader(
        topic='p2ptest_clients',
        channel='server',
        message_handler=functools.partial(on_update_client_status),
        nsqd_tcp_addresses=NSQD_TCP_ADDRESSES,
    )
    nsq.run()

if __name__ == '__main__':
    main(sys.argv)
