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


def main(args):
    log.write('request the client registration')
    error = _request_client_registration()
    if error is not None:
        log.error_exit(-1, 'failed to request the client registration: {}'.format(error))

    log.write('wait for the server-side client registration')
    error = _wait_for_registration_complete()
    if error is not None:
        log.error_exit(-1, 'failed to the client registration: {}'.format(error))

    log.write('start ContentServer')
    cv = content_server.ContentServer().start()
    time.sleep(3)
    cv.stop()

    '''
    utils.create_nsq_reader('p2ptest_jobs', _on_receive_jobs)
    nsq.run()
    '''


def _request_client_registration():
    data = protocols.registration(49152)

    # for debug
    import hostinfo
    import random
    data = data.replace(hostinfo.get_user(), str(random.randint(0, 100)))

    code, result = http.nsq_pub_sync('p2ptest_register_client', data)
    if code == 200 and result == 'OK':
        return None
    return result


def _wait_for_registration_complete():
    def _predicate(queries):
        if 'result' in queries:
            if len(queries['result']) == 1:
                return True
        return False

    result = http.wait_for_get_request(49152, _predicate)
    if result['result'][0] != 'OK':
        return result['result'][0]

    return None


def _on_receive_jobs(message):
    message.enable_async()
    log.write(message.body)
    message.finish()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
