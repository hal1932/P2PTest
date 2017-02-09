# encoding: utf-8
from __future__ import print_function

import config
import protocols
import http

import nsq

import sys
import functools

NSQD_HTTP_ADDRESS = '127.0.0.1:4151'
NSQD_TCP_ADDRESSES = ['127.0.0.1:4150', ]


def register_as_client():
    url = 'http://{}/pub?topic=p2ptest_clients'.format(config.NSQD_HTTP_ADDRESS)
    data = protocols.registration()
    response = http.post_sync(url, data)
    return response == 'OK'


def on_receive_jobs(message):
    message.enable_async()
    print(message.body)
    message.finish()


def main(args):
    if not register_as_client():
        return -1

    '''
    nsq.Reader(
        topic='p2ptest_jobs',
        channel='test',
        message_handler=on_receive_jobs,
        nsqd_tcp_addresses=NSQD_TCP_ADDRESSES,
    )
    nsq.run()
    '''

if __name__ == '__main__':
    result = main(sys.argv)
    sys.exit(result)
