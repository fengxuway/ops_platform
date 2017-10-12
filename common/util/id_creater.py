#!/usr/bin/python
# coding:utf-8
__author__ = 'Fengxu'

import random


import logging

log = logging.getLogger('django')

id_card = 10


def random_str(length=8):
    m = random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], length)
    return "".join(m)


def server_id(length=id_card):
    """
    server ID generator
    :param length:
    :return:
    """
    from server.models import Server

    s_id = "S-" + random_str(length-2)
    while True:
        try:
            Server.objects.get(server_id=s_id)
            log.error("server id<%s> exists! generate again..." % s_id)
        except Exception as e:
            break
    return s_id


def main():
    print((server_id()))


if __name__ == "__main__":
    main()
