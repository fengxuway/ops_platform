#!/usr/bin/env python
# coding:utf-8
import traceback
# from aliyunsdkcore import client
# from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
# from aliyunsdkecs.request.v20140526 import DescribeDisksRequest
# from aliyunsdkecs.request.v20140526 import DescribeRegionsRequest
# from aliyunsdkecs.request.v20140526 import DescribeEipAddressesRequest
# from aliyunsdkecs.request.v20140526 import DescribeVpcsRequest
# from aliyunsdkecs.request.v20140526 import DescribeVRoutersRequest
# from aliyunsdkcore.acs_exception.exceptions import ClientException
import json
from cmdb.models import ServerInfo
from service.logic import run_task
from celery.task import task
from service.logic import ansible_ip
import logging
from celery.schedules import crontab
from celery.task import periodic_task
from cmdb.util.ksyun_api import get_ksyun, update_group
from .ansible_host import AnsibleHostBuild
from cmdb.util.new_aliyun_api import Aliyun_api

log = logging.getLogger('worker')


region_beijing = 'cn-beijing'

'''
class Aliyun_api(object):
    """
    获取磁盘信息
    """
    def __init__(self, access_key, access_secret, region_id):
        self.AccessKey = access_key
        self.AccessSecret = access_secret
        self.RegionId = region_id
        self.format = 'json'
        self.clt = client.AcsClient(self.AccessKey, self.AccessSecret, self.RegionId)

    # DescribeRegions 查询查询可用地域列表
    def describe_regions_request(self):
        """
        DescribeRegions 查询所有地域
        :return:
        """
        request = DescribeRegionsRequest.DescribeRegionsRequest()
        request.set_accept_format(self.format)
        return request

    # DescribeInstances 查询所有实例的详细信息
    def describe_instances_request(self, instance_ids=None, page_number=1, page_size=100):
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format(self.format)
        request.set_PageSize(page_size)
        if instance_ids:
            request.set_InstanceIds(json.dumps(instance_ids))
        request.set_PageNumber(page_number)
        return request

    # DescribeDisks 查询磁盘信息
    def describe_disks_request(self, page_number=1, page_size=100):
        request = DescribeDisksRequest.DescribeDisksRequest()
        request.set_accept_format(self.format)
        request.set_PageSize(page_size)
        request.set_PageNumber(page_number)
        return request

    #
    def describe_eip_addresses_request(self, page_number=1, page_size=100):
        request = DescribeEipAddressesRequest.DescribeEipAddressesRequest()
        request.set_accept_format(self.format)
        request.set_PageSize(page_size)
        request.set_PageNumber(page_number)
        return request
    #
    def describe_vpcs_request(self, page_number=1, page_size=50):
        request = DescribeVpcsRequest.DescribeVpcsRequest()
        request.set_accept_format(self.format)
        request.set_PageSize(page_size)
        request.set_PageNumber(page_number)
        return request

    def describe_v_routers_request(self, page_number=1, page_size=50):
        request = DescribeVRoutersRequest.DescribeVRoutersRequest()
        request.set_accept_format(self.format)
        request.set_PageSize(page_size)
        request.set_PageNumber(page_number)
        return request

    def describe_load_balancers_request(self):
        request = DescribeLoadBalancersRequest.DescribeLoadBalancersRequest()
        request.set_accept_format(self.format)
        return request

    def do_action(self, request):
        return self.clt.do_action(request)

'''
def get_regions():
    """
    获取阿里云ECS地域信息
    :return:
    """
    log.info('Fetching all regions...')
    ali = Aliyun_api(region_beijing)
    region_request = ali.describe_regions_request()
    region_result = json.loads(ali.do_action(region_request))
    result = []
    for region in region_result['Regions']['Region']:
        result.append(region['RegionId'])
    log.info('Fetch regions success. Count: <%s>.' % len(result))
    return result

@task
def get_ali_servers(regionid='', instanceid=''):
    """
    获取阿里云ECS信息
    :param regionid: 指定区域ID将会更新对应区域下所有阿里云主机
    :param instanceid: 指定实例ID将仅更新指定阿里云主机
    :return:
    """
    log.info('Fetch instance from aliyun API starting...')
    if instanceid:
        log.info('Fetching one instance <%s>...' % instanceid)
        # 如果设置实例ID，则根据已存在的实例获取对应的区域ID
        si = ServerInfo.objects.safe_get(InstanceId=instanceid)
        if not si:
            log.error('Not found this instance!')
            return None
        # regions 用于记录要更新的主机所属的区域列表
        regions = [si.RegionId]
    elif regionid:
        log.info("Fetching instances from Region <%s>..." % regionid)
        # 如果设置区域ID，表示更新该区域下的所有实例
        regions = [regionid]
    else:
        log.info("Fetching all instances...")
        # 否则更新全部信息，先遍历所有的区域
        regions = get_regions()
    # 遍历当前可用的区域
    for reg in regions:
        # 默认页码
        page_num = 1
        ali = Aliyun_api(reg)
        while True:
            if instanceid:
                server_request = ali.describe_instances_request(instance_ids=[instanceid], page_number=page_num)
            else:
                server_request = ali.describe_instances_request(page_number=page_num)
            try:
                server_result = ali.do_action(server_request)
            except Exception as e:
                log.error("Aliyun Region [%s] Error" % reg)
                log.error(traceback.format_exc())
                break
            try:
                result = json.loads(server_result)
            except json.decoder.JSONDecodeError as je:
                log.error("fetch Aliyun region [ %s ] json Decode Error! response: \n----------\n%s \n--------- \n"
                          % (reg, server_result))
                break

            update_server(result, 'ECS')
            page_num += 1
            if result['PageNumber'] * result['PageSize'] >= result['TotalCount']:
                log.info("Region [%s] update <%s> instances." % (reg, result['TotalCount']))
                break
    log.info('Fetch Aliyun ECS instance complete!')
    for reg in regions:
        try:
            ali = Aliyun_api(reg, baseurl='https://slb.aliyuncs.com')
            request = ali.describe_load_balancers_request()
            response = ali.do_action(request)
            result = json.loads(response)
            update_server(result, 'SLB')
        except Exception as e:
            log.error("Aliyun LB Region [%s] Error" % reg)
            log.error(traceback.format_exc())
            continue


# 更新阿里云ECS信息到数据库中
def update_server(result, instance_type):
    """
    解析结果，写入更新到ServerInfo数据库
    :param result: ecs请求的结果
    :param instance_type:
    :return:
    """

    if instance_type == 'ECS' and 'Instances' in result:
        for inst in result['Instances']['Instance']:
            eip = []
            if 'IpAddress' in inst['EipAddress'] and inst['EipAddress']['IpAddress']:
                eip.append(inst['EipAddress']['IpAddress'])
            ip_type = 'default'
            if inst['VpcAttributes']['PrivateIpAddress']['IpAddress']:
                ip_type = 'vpc'
            PublicIpAddress = '|'.join(inst['PublicIpAddress']['IpAddress'] + eip)
            InnerIpAddress = '|'.join(inst['InnerIpAddress']['IpAddress']
                                      + inst['VpcAttributes']['PrivateIpAddress']['IpAddress'])
            si = ServerInfo.objects.safe_get(InstanceId=inst['InstanceId'])
            if si:
                si.RegionId = inst['RegionId']
                si.ZoneId = inst['ZoneId']
                si.InstanceName = inst['InstanceName']
                si.InstanceType = instance_type
                si.PublicIpAddress = PublicIpAddress
                si.InnerIpAddress = InnerIpAddress
                si.Status = inst['Status']
                si.Cpu = inst['Cpu']
                si.Memory = inst['Memory']
                si.InternetMaxBandwidthOut = inst['InternetMaxBandwidthOut']
                si.InternetMaxBandwidthIn = inst['InternetMaxBandwidthIn']
                si.server_location = 'aliyun'
                si.IpType = ip_type
            else:
                si = ServerInfo(
                    RegionId=inst['RegionId'],
                    ZoneId=inst['ZoneId'],
                    InstanceId=inst['InstanceId'],
                    InstanceName=inst['InstanceName'],
                    InstanceType='ECS',
                    PublicIpAddress=PublicIpAddress,
                    InnerIpAddress=InnerIpAddress,
                    Status=inst['Status'],
                    Cpu=inst['Cpu'],
                    Memory=inst['Memory'],
                    InternetMaxBandwidthOut=inst['InternetMaxBandwidthOut'],
                    InternetMaxBandwidthIn=inst['InternetMaxBandwidthIn'],
                    server_location='aliyun',
                    IpType=ip_type
                )
                si.save()

            update_group(si)
            si.save()
    elif instance_type == 'SLB':
        for inst in result['LoadBalancers']['LoadBalancer']:
            """
            {
                "RegionIdAlias": "cn-beijing",
                "Address": "60.205.109.46",
                "AddressType": "internet",
                "LoadBalancerStatus": "active",
                "LoadBalancerName": "bj-ali-g2-mqtt-01",
                "SlaveZoneId": "cn-beijing-b",
                "RegionId": "cn-beijing-btc-a01",
                "MasterZoneId": "cn-beijing-a",
            },
            """
            si = ServerInfo.objects.safe_get(InstanceId=inst['LoadBalancerId'])
            InnerIpAddress = PublicIpAddress = ''
            if inst['AddressType'] == 'internet':
                PublicIpAddress = inst['Address']
            else:
                InnerIpAddress = inst['Address']
            if si:
                si.RegionId = inst['RegionIdAlias']
                si.ZoneId = inst['MasterZoneId']
                si.InstanceName = inst['LoadBalancerName']
                si.InstanceType = instance_type
                si.PublicIpAddress = PublicIpAddress
                si.InnerIpAddress = InnerIpAddress
                si.Status = inst['LoadBalancerStatus']
                # si.InternetMaxBandwidthOut = inst['InternetMaxBandwidthOut']
                # si.InternetMaxBandwidthIn = inst['InternetMaxBandwidthIn']
                si.server_location = 'aliyun'
                si.IpType = 'default'
            else:
                si = ServerInfo(
                    RegionId=inst['RegionIdAlias'],
                    ZoneId=inst['MasterZoneId'],
                    InstanceId=inst['LoadBalancerId'],
                    InstanceName=inst['LoadBalancerName'],
                    InstanceType=instance_type,
                    PublicIpAddress=PublicIpAddress,
                    InnerIpAddress=InnerIpAddress,
                    Status=inst['LoadBalancerStatus'],
                    # InternetMaxBandwidthOut=inst['InternetMaxBandwidthOut'],
                    # InternetMaxBandwidthIn=inst['InternetMaxBandwidthIn'],
                    server_location='aliyun',
                    IpType='default'
                )
                si.save()
            update_group(si)
            si.save()


@task
def get_ali_disk_info(regionid=''):
    """
    获取阿里云磁盘信息
    :param regionid: 地域id
    :return:
    """
    log.info('Fetch aliyun disk info starting...')
    try:
        if regionid == "":
            ali = Aliyun_api('cn-beijing')
            request = ali.describe_regions_request()
            regions_res = json.loads(ali.do_action(request))
            for i in regions_res['Regions']['Region']:  # 循环地域
                cycle_disk_info(i['RegionId'])
        else:
            cycle_disk_info(regionid)
        log.info('Fetch aliyun disk info complete!')
    except Exception:
        log.error('Fetch aliyun disk got Error: ')
        traceback.print_exc()


def cycle_disk_info(regionid):
    """
    解耦出来循环阿里云磁盘信息的函数
    :param regionid: 地域
    :return:
    """
    try:
        ali_all = Aliyun_api(regionid)
        page_num = 1
        disk_map = {}
        while True:
            _request = ali_all.describe_disks_request(page_number=page_num)
            disk_res = json.loads(ali_all.do_action(_request))

            for disk in disk_res['Disks']['Disk']:
                _instanceid = disk['InstanceId']
                _size = disk['Size']
                _category = disk['Category']
                if _category == 'cloud_efficiency':
                    _category = 'EFFICIENCY'
                elif _category == 'cloud_ssd':
                    _category = "SSD"
                else:
                    _category = "SATA"
                disk_map.setdefault(_instanceid, {"DiskSize": 0, "DiskType": "SATA"})
                disk_map[_instanceid]['DiskSize'] += _size
                if _category != 'SATA':
                    disk_map[_instanceid]['DiskType'] = _category

            page_num += 1
            if disk_res['PageNumber'] * disk_res['PageSize'] >= disk_res['TotalCount']:
                break
        for instance_id, disk in list(disk_map.items()):
            si = ServerInfo.objects.safe_get(InstanceId=instance_id)
            if si:
                si.DiskSize = disk['DiskSize']
                si.DiskType = disk['DiskType']
                si.save()
    except Exception:
        traceback.print_exc()



@task
def update_server_info(srvs):
    """
    更新cmdb页面选中服务器，并更新服务器信息到ServerInfo表中
    :param
    :param
    :return:
    """
    li_aliyun = []   # 阿里云主机列表
    li_ksyun = []    # 金山云主机列表
    srv_obj = ServerInfo.objects.filter(id__in=srvs)
    for srv in srv_obj:
        server_location = srv.server_location
        if server_location == "ksyun":  # 过滤出金山云的server
            li_ksyun.append(srv.id)
        elif server_location == "aliyun":  # 过滤出阿里云的server
            li_aliyun.append(srv.id)
    if li_ksyun:
        update_ksyun_info(li_ksyun)  # 更新金山云KEC
    if li_aliyun:
        update_ail_info(li_aliyun)  # 更新阿里云ECS
    save_ansible_info(srvs)  # 更新选中server的 ansible_host 信息
    ansible_sync_server(srvs)  # 更新选中server的更详细信息

def update_ail_info(srv):
    """
    更新阿里云api信息
    """
    try:
        for srv_id in srv:
            srv_obj = ServerInfo.objects.get(id=srv_id)
            instance_id = srv_obj.InstanceId
            if instance_id:
                get_ali_servers(instanceid=instance_id)  # 更新阿里云信息
    except Exception:
        traceback.print_exc()

def update_ksyun_info(srv):
    """
    更新金山云api信息
    """
    try:
        for srv_id in srv:
            srv_obj = ServerInfo.objects.get(id=srv_id)
            instance_id = srv_obj.InstanceId
            if instance_id:
                get_ksyun(instance_id=instance_id)  # 更新金山云信息
    except Exception:
        traceback.print_exc()


def save_ansible_info(srv=None):
    """
    保存ansible host到数据库中
    """
    AnsibleHostBuild(srv).execute()


def ansible_sync_server(srv=None):
    """
    使用ansibleAPI的SETUP模块获取服务器详情
    :param srv: ServerInfo列表
    :return:
    """
    print("START ansible sync server!")
    server_data = {}
    ansible_hosts = []
    if not srv:
        srvs = ServerInfo.objects.filter(InstanceType__in=['ECS', 'KEC'])

    else:
        srvs = ServerInfo.objects.filter(InstanceType__in=['ECS', 'KEC'], id__in=srv)
    for si in srvs:
        if si.ansible_host:
            ip = ansible_ip(si.ansible_host)
            ansible_hosts.append(si.ansible_host)
            server_data.setdefault(ip, {"ansible_host": si.ansible_host,
                                        "server_id": si.id,
                                        "server_location": si.server_location,
                                        })
    if not ansible_hosts:
        return None
    print(ansible_hosts)
    result = run_task(ansible_hosts, module_name='setup')
    for ip, _result in list(result.items()):
        # si = server_data[ip]['server']
        si = ServerInfo.objects.safe_get(id=server_data[ip]['server_id'])
        _r = _result['result']
        if _result['status'] != 'ok':
            print(("ERROR", _r))
            continue
        facts = _r['ansible_facts']
        if server_data[ip]['server_location'] == 'aliyun':
            si.os = facts['ansible_distribution']
            si.os_release = facts['ansible_distribution_release']
            si.os_version = facts['ansible_distribution_version']
            si.Cpu_info = facts['ansible_processor'][1]
            si.sys_bits = facts['ansible_machine']
            # memory = facts['ansible_devices']['sda']['size']
            # cpu = facts['ansible_processor_cores']

            si.save()
        else:
            si.os = facts['ansible_distribution']
            si.os_release = facts['ansible_distribution_release']
            si.os_version = facts['ansible_distribution_version']
            si.Cpu_info = facts['ansible_processor'][1]
            si.sys_bits = facts['ansible_machine']
            si.Cpu = facts['ansible_processor_cores']
            si.Memory = facts['ansible_memtotal_mb']
            si.InstanceName = facts['ansible_nodename']
            si.DiskSize = sum([i['size_total'] for i in facts['ansible_mounts']]) / 1024.0 / 1024 / 1024
            si.save()


def ansible_get_all_server_info():
    """
    通过ansible获取所有服务器信息(用于每天计划任务定时更新)
    """
    log.info('Ansible fetch data starting...')
    try:
        # li_srv_id = [srv.id for srv in ServerInfo.objects.all()]
        save_ansible_info()    # 添加ansible_host到数据库中
        ansible_sync_server()  # 从含有ansible_host信息的服务器上获取数据，并存到数据中
        log.info('Ansible fetch complete!')
    except Exception:
        traceback.print_exc()


# @periodic_task(run_every=(crontab(minute=30, hour=2)))
@task
def cron_update():
    """
    每天计划任务定时 2:30 更新阿里云ECS及金山云KEC信息
    """
    # get_ali_servers()    # 获取阿里云 硬盘信息
    # log.info('===================')
    # get_ali_disk_info()  # 获取阿里云 ECS信息
    # log.info('===================')
    # get_ksyun()  # 获取金山云 KEC全部信息
    # log.info('===================')
    ansible_get_all_server_info()  # 通过ansible获取服务器更详细信息


# @periodic_task(run_every=(crontab(minute=54, hour='*')))
@task
def cron_update_ali_ksyun_api():
    """
    只更新阿里云&金山云API接口, 每小时一次
    """
    get_ali_servers()
    get_ali_disk_info()
    get_ksyun()


def main():
    get_ali_disk_info()
    get_ali_servers()


if __name__ == '__main__':
    main()
