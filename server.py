# encoding: utf-8
import client_pool

import nsq

import sys


def main(args):
    pool = client_pool.ClientPool()
    pool.start_accepting_clients()

    nsq.run()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
