# encoding: utf-8
from __future__ import print_function

import hostinfo
import http

import sys

NSQD_HTTP_ADDRESS = '127.0.0.1:4151'
NSQD_TCP_ADDRESSES = ['127.0.0.1:4150', ]


def register_as_client():
    url = 'http://{}/pub?topic=p2ptest_clients'.format(NSQD_HTTP_ADDRESS)
    data = {
        'host': hostinfo.get_ipv4_address(),
        'user': hostinfo.get_user(),
    }
    http.post_sync(url, data)


def main(args):
    register_as_client()

if __name__ == '__main__':
    main(sys.argv)
