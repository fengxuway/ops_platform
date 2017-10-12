#!/usr/bin/python
# coding:utf-8
import os
import subprocess
from django.conf import settings
import logging


log = logging.getLogger('scripts')


shell_dir = os.path.join(settings.BASE_DIR, 'scripts')
_ssh_copy_id_passwd = os.path.join(shell_dir, 'ssh-copy-id-passwd')
os.chmod(_ssh_copy_id_passwd, 0o555)


def ssh_copy_id_passwd(ip, user, password, port):
    """
    command ssh_copy_ip_passwd
    :param ip: IP address
    :param user: ssh user
    :param password: ssh password
    :param port: ssh port
    :return:
    """
    if not password:
        sh = 'ssh-copy-id -i ~/.ssh/id_rsa.pub %s@%s -p %s' % (user, ip, port)
    else:
        sh = '%s -i ~/.ssh/id_rsa.pub "sshpass -p %s ssh -p %s %s@%s"' % (_ssh_copy_id_passwd, password, port, user, ip)
    log.info("Try to connect server: %s@%s -p %s" % (user, ip, port))
    log.info(">>> " + sh)
    result = subprocess.getstatusoutput(sh)
    log.info('result: ' + str(result))
    return result


def main():
    ssh_copy_id_passwd('192.168.11.10', 'root', '123', 22)


if __name__ == "__main__":
    main()
