# encoding: utf-8
import config

import nsq

import sys


def nop(*args, **kwargs):
    pass


def create_nsq_writer():
    return nsq.Writer(config.NSQD_TCP_ADDRESSES)


def create_nsq_reader(topic, message_handler, channel='default'):
    return nsq.Reader(
        topic=topic,
        channel=channel,
        message_handler=message_handler,
        nsqd_tcp_addresses=config.NSQD_TCP_ADDRESSES,
    )
