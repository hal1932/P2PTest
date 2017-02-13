# encoding: utf-8
from __future__ import print_function

import sys
import datetime


def write(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print('[{}] {}'.format(time, message))


def debug(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print('[{}] [DEBUG] {}'.format(time, message))


def warning(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print('[{}] [WARNING] {}'.format(time, message), file=sys.stderr)


def error(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print('[{}] [ERROR] {}'.format(time, message), file=sys.stderr)


def error_exit(status, message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print('[{}] [ERROR] {}'.format(time, message), file=sys.stderr)
    sys.exit(status)
