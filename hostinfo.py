# encoding: utf-8

import sys
import netifaces
import getpass


def get_ipv4_address():
    if sys.platform == 'win32':
        iface = netifaces.interfaces()
        ifaddress = netifaces.ifaddresses(iface[0])
    elif sys.platform == 'darwin':
        ifaddress = netifaces.ifaddress('en0')
    else:
        raise NotImplementedError()

    return ifaddress.get(netifaces.AF_INET)[0]['broadcast']


def get_user():
    return getpass.getuser()
