# encoding: utf-8
import config
import protocols
import http
import content_server
import log
import utils

import nsq

import sys
import functools
import time
import random


def main(args):
    log.write('request the client registration')
    notification_port, content_port, error = _request_client_registration()
    if error is not None:
        log.error_exit(-1, 'failed to request the client registration: {}'.format(error))

    log.write('wait for the server-side client registration at port {}'.format(notification_port))
    error = _wait_for_registration_complete(notification_port)
    if error is not None:
        log.error_exit(-1, 'failed to the client registration: {}'.format(error))

    log.write('start ContentServer at port {}'.format(content_port))
    cv = content_server.ContentServer(content_port).start()
    time.sleep(3)
    cv.stop()

    '''
    utils.create_nsq_reader('p2ptest_jobs', _on_receive_jobs)
    nsq.run()
    '''


def _request_client_registration():
    notification_port = random.randint(
        config.PEER_CONTENT_PORT_BASE,
        config.PEER_CONTENT_PORT_MAX - 1)
    content_port = notification_port + 1
    data = protocols.registration(notification_port, content_port)

    # for debug
    import hostinfo
    data = data.replace(hostinfo.get_user(), str(random.randint(0, 100)))

    code, result = http.nsq_pub_sync('p2ptest_register_client', data)
    if code == 200 and result == 'OK':
        return notification_port, content_port, None

    return 0, 0, result


def _wait_for_registration_complete(notification_port):
    def _predicate(queries):
        if 'result' in queries:
            if len(queries['result']) == 1:
                return True
        return False

    result = http.wait_for_get_request(notification_port, _predicate)
    if result['result'][0] != 'OK':
        return result['result'][0]

    return None


def _on_receive_jobs(message):
    message.enable_async()
    log.write(message.body)
    message.finish()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
