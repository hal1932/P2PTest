# encoding: utf-8
import pycurl

import StringIO
import json


def get_sync(url):
    response = StringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.WRITEDATA, response)
    c.perform()

    return response.getvalue()


def post_sync(url, data):
    response = StringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.POSTFIELDS, data)
    c.setopt(pycurl.WRITEDATA, response)
    c.perform()

    return response.getvalue()
