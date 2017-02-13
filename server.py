# encoding: utf-8
import client_query_server
import client_pool
import client_accessor

import nsq

import sys


# TODO: サーバが落ちると接続中クライアントの一覧が失われるので、復帰処理を追加する

def main(args):
    query_server = client_query_server.ClientQueryRequestServer(12345)
    query_server.start()

    pool = client_pool.ClientPool(query_server)
    pool.start_accepting_clients()

    accessor = client_accessor.ClientAccessor(query_server, pool)
    accessor.start_accepting_query()

    nsq.run()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
