#!/usr/bin/python
# coding:utf-8
import logging
import traceback
from datetime import datetime

from celery.task import task
from django.db.models import ObjectDoesNotExist

from common.util.des import decrypt
from common.util.shell_util import ssh_copy_id_passwd
from server.models import Server
from service.logic import run_task, ansible_ip
from cmdb.models import ServerInfo

log = logging.getLogger('ansible')

@task
def connect_server(srv_id):
    try:
        srv = ServerInfo.objects.get(id=srv_id)
        srv.connect = 1
        srv.save()
    except ObjectDoesNotExist as e:
        log.error("Server<%s> not Found!" % srv_id)
        raise e

    try:
        logs = srv.connect_log if srv.connect_log else ''
        passwd = decrypt(srv.pwd)

        for ip_addr in [srv.InnerIpAddress, srv.PublicIpAddress]:
            if ip_addr:
                result = ssh_copy_id_passwd(ip_addr, srv.user, passwd, srv.port)
                logs += '\n\n\n' + '*' * 80 \
                        + '\n[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] 测试连接IP：[%s] ' % ip_addr \
                        + '\n' + '-' * 40 + '\n' + result[1]
                if result[0] == 0:
                    log.info("Connect Success!")
                    logs += '-' * 40 + '\n<b>连接成功！</b>\n' + '*' * 80
                    srv.connect = 2
                    srv.connect_log = logs
                    srv.ansible_host = ip_addr
                    srv.ansible_host += ' ansible_ssh_user=' + srv.user
                    if srv.port != 22:
                        srv.ansible_host += ' ansible_ssh_port=' + str(srv.port)
                    srv.save()
                    break
                else:
                    log.info("Connect Error!" + result[1])
                    logs += '-' * 40 + '\n<b>连接失败！</b>'
                    srv.connect = -1
                    srv.connect_log = logs
                    srv.save()

        # ansible通过setup模块获取server基本信息
        if srv.connect == 2:
            ansible_setup.delay(srv)
            return True
    except Exception:
        srv.connect = -1
        srv.save()
        log.error("connect got Error: \n" + traceback.format_exc())
    return False


@task
def ansible_setup(server):
    """
    ansible执行setup模块获取目标主机的基本信息
    :param server:
    :return:
    """
    if server.connect == 2:
        setup_data = run_task([server.ansible_host], module_name='setup')
        ip = ansible_ip(server.ansible_host)
        if setup_data[ip]['status'] == 'ok':
            data = setup_data[ip]['result']
            facts = data['ansible_facts']
            server.hostname = facts['ansible_hostname']
            server.os = facts['ansible_distribution']
            server.memory = facts['ansible_memory_mb']['real']['total']
            server.memory_free = facts['ansible_memory_mb']['real']['free']
            server.save()


def main():
    pass


if __name__ == "__main__":
    main()
