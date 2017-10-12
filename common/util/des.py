#!/usr/bin/python
# coding:utf-8
__author__ = 'Fengxu'

from pyDes import *
from django.conf import settings
# from ntdeploy import settings
import traceback
import logging
import base64


log = logging.getLogger('django')
k = des(settings.DES_KEY, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)


def encrypt(s):
    """
    encrypt password by 3DES
    :param s:
    :return:
    """
    try:
        if not s:
            return ''
        if isinstance(s, str):
            s = s.encode("utf-8")
        des = k.encrypt(s)
        return base64.encodestring(des)
    except Exception as e:
        log.error(traceback.format_exc())
        raise e


def decrypt(s):
    """
    decrypt password by 3DES
    :param s:
    :return:
    """
    try:
        des = base64.decodestring(s)
        return k.decrypt(des, padmode=PAD_PKCS5)
    except Exception as e:
        log.error(traceback.format_exc())
        raise e


def main():
    s = '123'
    s2 = encrypt(s)
    s3 = decrypt(s2)
    print(s2, s3, type(s3))



if __name__ == "__main__":
    main()
