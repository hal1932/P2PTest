# encoding: utf-8


class ClientInfo(object):

    def __init__(self, host, user, content_port):
        self.__host = host
        self.__user = user
        self.__content_port = content_port

    @property
    def host(self):
        return self.__host

    @property
    def user(self):
        return self.__user

    @property
    def ping_url(self):
        return self.content_url + '/ping'

    @property
    def content_url(self):
        return 'http://{}:{}'.format(self.host, self.__content_port)
