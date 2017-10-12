#!/usr/bin/env python
# coding:utf-8
from cmdb.models import ServerInfo
from service.logic import run_task
import logging
from django.db.models import Q
import datetime


log = logging.getLogger('ansible')


class AnsibleHostBuild(object):
    """
    更新Ansible_Host字段信息
    """

    def __init__(self, server_ids=None):
        self.server_ids = server_ids
        self.instance_list = []
        self.ip_list = {}
        # 是否尝试连接公网IP
        self.fetch_public_ip = True

        self.init_data()

    def filter_connected(self):
        """
        过滤掉已经可以通过`ansible_host`字段直接连接的服务器
        :return:
        """
        if not self.server_ids:
            servers = ServerInfo.objects.filter(InstanceType__in=['ECS', 'KEC']).filter(enabled=0, connect=0,
                                                update_time__gt=datetime.datetime.utcnow() - datetime.timedelta(hours=64))
        else:
            servers = ServerInfo.objects.filter(id__in=self.server_ids, InstanceType__in=['ECS', 'KEC'])
        '''
        inv = [srv.ansible_host for srv in servers if srv.ansible_host]
        if inv:
            ping_result = run_task(inv, module_name='ping')
            connected_ips = []
            for ip, result in list(ping_result.items()):
                if result['status'] == 'ok' and result['result']['ping'] == 'pong':
                    connected_ips.append(ip)
                    log.info("ping <%s> pong!" % ip)

            not_connected = servers.exclude(
                Q(InnerIpAddress__in=connected_ips) | Q(PublicIpAddress__in=connected_ips))
            return not_connected
        else:
            return servers
        '''
        return servers


    def init_data(self):
        """
        构造ip列表和server的实例字典
        :return:
        """
        servers = self.filter_connected()

        for srv in servers:
            tmp = [srv.id]
            if srv.InnerIpAddress:
                tmp.extend(srv.InnerIpAddress.split('|'))
            if self.fetch_public_ip and srv.PublicIpAddress:
                tmp.extend(srv.PublicIpAddress.split('|'))
            self.instance_list.append(tmp)
            if self.fetch_public_ip:
                ip_list = srv.InnerIpAddress.split('|') + srv.PublicIpAddress.split('|')
            else:
                ip_list = srv.InnerIpAddress.split('|')
            for ip in ip_list:
                if ip:
                    user = srv.user if srv.user else 'root'
                    port = srv.port if srv.port else 8022
                    pwd = srv.pwd if srv.pwd else ''
                    self.ip_list[ip] = {'id': srv.id, 'user': user, 'port': port, 'pwd': pwd}
                    '''
                    self.instance_list = [
                        ['i-1', 11, 12, 13],
                        ['i-2', 21, 22, 23, 25],
                        ['i-3', 33, 34],
                        ['i-5', 50],
                    ]
                    self.ip_list = {
                        11: {"id": 'i-1', "user": 'root', 'port': 8022, 'pwd': ''},
                        12: {"id": 'i-1', "user": 'root', 'port': 8022},
                        13: {"id": 'i-1', "user": 'root', 'port': 8022},
                        21: {"id": 'i-2', "user": 'root', 'port': 8022},
                        22: {"id": 'i-2', "user": 'root', 'port': 8022},
                        23: {"id": 'i-2', "user": 'root', 'port': 8022},
                        25: {"id": 'i-2', "user": 'root', 'port': 8022},
                        33: {"id": 'i-3', "user": 'root', 'port': 8022},
                        34: {"id": 'i-3', "user": 'root', 'port': 8022},
                        50: {"id": 'i-5', "user": 'root', 'port': 8022},
                    }
                    '''

    def format_ansible_host(self, ip, data_switch=None):
        """
        根据IP地址生成ansible_host字符串
        :param ip:
        :param data_switch:
        :return:
        """
        data = self.merge_ansible_data(ip, data_switch)
        if data['pwd']:
            return '{ip} ansible_user={user} ansible_port={port} ansible_ssh_pass={pwd}'.format(ip=ip, **data)
        else:
            return '{ip} ansible_user={user} ansible_port={port}'.format(ip=ip, **data)

    def merge_ansible_data(self, ip, data_switch):
        """
        合并data_switch中数据到默认SSH连接数据中
        :param ip: IP Address, 包含外网内网IP
        :param data_switch: {"port": 22, "pwd": ''}
        :return:
        """
        data = self.ip_list[ip].copy()
        if data_switch:
            data['pwd'] = data_switch['pwd']
            data['port'] = data_switch['port']
        return data

    def clear_instances(self, remove_ip):
        """
        清理已经获取到host的主机
        :param remove_ip: 要清理的主机的ip列表
        :return:
        """
        print("prepare delete: ", remove_ip)
        for i in range(len(self.instance_list) - 1, -1, -1):
            for ri in remove_ip:
                if ri in self.instance_list[i]:
                    print("deleting: ", self.instance_list[i])
                    self.instance_list.remove(self.instance_list[i])
                    break

            # if self.instance_list[i][0] in remove_ip:
            #     print("deleting: ", self.instance_list[i])
            #     self.instance_list.remove(self.instance_list[i])

        # for k in range(0, len(self.instance_list)):
        #     if self.instance_list[k][0] in remove_ip:
        #         del (self.instance_list[k])

    def execute(self):
        log.info("Start fetch Ansible Host...")
        """
        执行更新ansible Host任务
        :return:
        """
        # guess_connect_args = [None, {'port': 8022, 'pwd': ''}, {'port': 8022, 'pwd': '__password__'},
        #                {'port': 22, 'pwd': ''}, {'port': 22, 'pwd': '__password__'}]
        # 尝试连接逻辑，仅测试8022端口公钥认证
        guess_connect_args = [{'port': 8022, 'pwd': ''}]

        for switch in guess_connect_args:
            _max = max([len(i) for i in self.instance_list])
            log.info("开始初始化ansible-host: " +  str(switch))
            for i in range(1, _max):
                inv = [self.format_ansible_host(line[i], switch) for line in self.instance_list if len(line) > i and line[i]]
                ping_result = run_task(inv, module_name='ping')
                remove_ips = []
                for ip, result in list(ping_result.items()):
                    if result['status'] == 'ok' and result['result']['ping'] == 'pong':
                        si = ServerInfo.objects.safe_get(id=self.ip_list[ip]['id'])
                        si.ansible_host = self.format_ansible_host(ip, switch)
                        switch_data = self.merge_ansible_data(ip, switch)
                        si.connect = 1
                        si.port = switch_data['port']
                        si.user = switch_data['user']
                        si.pwd = switch_data['pwd']
                        si.save()
                        remove_ips.append(ip)
                        log.info("ping <%s> pong!" % ip)
                self.clear_instances(remove_ips)

        log.warning("连接失败的服务器: " + str(self.instance_list))
        for err_list in self.instance_list:
            srvs = ServerInfo.objects.filter(Q(PublicIpAddress__in=err_list) | Q(InnerIpAddress__in=err_list))
            if srvs:
                srvs.update(connect=0)

        log.info("Ansible Host fetch complete!")


def main():
    pass


if __name__ == '__main__':
    main()
