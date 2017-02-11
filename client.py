# encoding: utf-8
from __future__ import print_function

import config
import protocols
import http
import content_server

import nsq

import sys
import functools
import time

NSQD_HTTP_ADDRESS = '127.0.0.1:4151'
NSQD_TCP_ADDRESSES = ['127.0.0.1:4150', ]


def main(args):
    if not _register_as_client():
        return -1

    server = content_server.ContentServer(1234)
    server.start()

    time.sleep(5)
    server.stop()

    '''
    nsq.Reader(
        topic='p2ptest_jobs',
        channel='test',
        message_handler=_on_receive_jobs,
        nsqd_tcp_addresses=NSQD_TCP_ADDRESSES,
    )
    nsq.run()
    '''


def _register_as_client(content_port):
    url = 'http://{}/pub?topic=p2ptest_clients'.format(config.NSQD_HTTP_ADDRESS)
    data = protocols.registration(content_port)
    response = http.post_sync(url, data)
    return response == 'OK'


def _on_receive_jobs(message):
    message.enable_async()
    print(message.body)
    message.finish()


if __name__ == '__main__':
    result = main(sys.argv)
    sys.exit(result)
