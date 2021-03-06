# encoding: utf-8

NSQD_HTTP_ADDRESS = '127.0.0.1:4151'
NSQD_TCP_ADDRESSES = ['127.0.0.1:4150', ]

# CONTENT以外にも使えるように前後100ずつ空けとく
PEER_CONTENT_PORT_BASE = 49152 + 100
PEER_CONTENT_PORT_MAX = 65535 - 100

PEER_CONTENT_ROOT = ''

MAX_PEER_COUNT = 100

PEER_PING_TIMEOUT = 5

TOPIC_REGISTER_CLIENT = 'p2ptest_register_client'

QUERY_CLIENTS_FINDALL = 'find_all'
