#!/usr/bin/env python
# coding=utf-8
import json
import os
import jinja2
import random
from common.util.ansible_api import Runner
from server.models import Server
import configparser
import logging
import traceback
from django.conf import settings
from celery.task import task
from django.core.exceptions import ObjectDoesNotExist
from common.util.ansible_api import ResultsCollector
from collections import OrderedDict
from cmdb.models import ServerInfo
from django.http import JsonResponse

log = logging.getLogger('ansible')

base_dir = settings.BASE_DIR


def run_task(inventory, module_name='command', module_args='', pattern='all'):
    """
    运行ansible单个任务
    :param inventory: 主机列表。格式：{'section1':['ip1', 'ip2',...], 'section2':[...]}
    :param pattern: 主机列表名
    :param module_name: 模块名
    :param module_args: 模块参数
    :return: task运行结果
    """
    if not inventory:
        raise Exception("No host selected!")
    task_name = 'default_task'
    task_list = [Runner.Task(task_name, module_name, module_args)]


    # 定义playbook对象
    p2 = Runner.Playbook(task_list=task_list)

    # 执行playbook
    runner = Runner(playbook=p2, host_list=inventory, pattern=pattern)
    # 执行单个任务或多个任务
    code, result = runner.run()
    # print(result)
    return result[task_name]


def random_str(length=8):
    m = random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], length)
    return "".join(m)


def format_result(result):
    log_result = {}.fromkeys(list(result.keys()), '')
    for key, val in list(result.items()):
        log_result[key] += '日志: \n' + val['detail']
        log_result[key] += '\n结果：\n[%s]' % key + "ok: %d, falures: %d, changed %d, skipped: %d, unreachable %d" % \
                                  (val['ok'], val['failures'], val['changed'], val['skipped'], val['unreachable'])
        print(log_result[key])
    return log_result


def main():
    pass


def ansible_ip(ansible_host):
    """
    ansible库获取IP地址
    将数据库server表ansible_host获取到对应的IP地址
    用于解析任务结果
    :param ansible_host: like "192.168.30.231 ansible_ssh_user=root"
    :return: IP Addr like "192.168.30.231"
    """
    analyze_ip = lambda ip: ip[0:ip.find(' ')] if ip.find(' ') > 0 else ip

    if isinstance(ansible_host, list):
        return [analyze_ip(i) for i in ansible_host]
    elif isinstance(ansible_host, str):
        return analyze_ip(ansible_host)
    return None


if __name__ == '__main__':
    main()
