# encoding: utf-8
from __future__ import print_function

import sys
import datetime


def write(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    print('[{}] {}'.format(time, message))


def warning(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def error(message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def error_exit(status, message):
    time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    sys.exit(status)
