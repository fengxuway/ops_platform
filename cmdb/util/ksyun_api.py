#!/usr/bin/env python
# coding:utf-8
import sys, datetime, hashlib, hmac, json, re
import requests
from urllib.parse import quote
from abc import ABCMeta
from cmdb.models import ServerInfo, ServerGroup, KsyEip
import traceback
import logging
from celery.task import task

log = logging.getLogger('worker')

access_key = "__access_key__"
secret_key = "__secret_key__"

class API(object, metaclass=ABCMeta):
    def execute(self):
        return KSYun(self).execute()


class DescribeInstances(API):
    def __init__(self, marker=0, max_results=100, instance_id=None, region='cn-beijing-6'):
        params = {'Action': 'DescribeInstances', 'Marker': marker, 'MaxResults': max_results,
                  'Version': '2016-03-04'}
        if instance_id:
            params['Filter.1.Name'] = 'instance-id'
            if isinstance(instance_id, str):
                params['Filter.1.Value.1'] = instance_id
            elif isinstance(instance_id, list):
                _count = 1
                for _id in instance_id:
                    params['Filter.1.Value.%s' % _count] = _id
                    _count += 1
        self.request_parameters = '&'.join(
            ["%s=%s" % (_key, quote(str(params[_key]))) for _key in sorted(params.keys())])

        self.method = 'GET'
        self.service = 'kec'
        self.region = region
        if region == 'cn-beijing-6':
            # self.endpoint = 'https://kec.api.ksyun.com'
            self.host = 'kec.api.ksyun.com'
        else:
            self.host = 'kec.%s.api.ksyun.com' % region
        self.endpoint = 'https://' + self.host



class DescribeSlb(API):
    def __init__(self, marker=0, max_results=100, instance_id=None, region='cn-beijing-6'):
        params = {'Action': 'DescribeLoadBalancers', 'Marker': marker, 'MaxResults': max_results,
                  'Version': '2016-03-04'}
        if instance_id:
            params['Filter.1.Name'] = 'instance-id'
            if isinstance(instance_id, str):
                params['Filter.1.Value.1'] = instance_id
            elif isinstance(instance_id, list):
                _count = 1
                for _id in instance_id:
                    params['Filter.1.Value.%s' % _count] = _id
                    _count += 1
        self.request_parameters = '&'.join(
            ["%s=%s" % (_key, quote(str(params[_key]))) for _key in sorted(params.keys())])

        self.method = 'GET'
        self.service = 'slb'
        self.region = region
        if region == 'cn-beijing-6':
            # self.endpoint = 'https://kec.api.ksyun.com'
            self.host = 'slb.api.ksyun.com'
        else:
            self.host = 'slb.%s.api.ksyun.com' % region
        self.endpoint = 'https://' + self.host



class DescribeAddresses(API):
    def __init__(self, next_token='', max_results=100, network_interface_id=None, region='cn-beijing-6'):
        """
        弹性IP列表API对象
        :param next_token: 下一页的token值,使用上次传回的NextToken值
        :param max_results: 每页数量
        :param network_interface_id: 网卡接口ID, 用于查询指定实例的IP地址
        """
        params = {'Action': 'DescribeAddresses', 'MaxResults': max_results, 'Version': '2016-03-04'}
        if network_interface_id:
            params['Filter.1.Name'] = 'network-interface-id'
            if isinstance(network_interface_id, str):
                params['Filter.1.Value.1'] = network_interface_id
            elif isinstance(network_interface_id, list):
                _count = 1
                for _id in network_interface_id:
                    params['Filter.1.Value.%s' % _count] = _id
                    _count += 1
        if next_token:
            params['NextToken'] = next_token
        self.request_parameters = '&'.join(
            ["%s=%s" % (_key, quote(str(params[_key]))) for _key in sorted(params.keys())])

        self.method = 'GET'
        self.service = 'eip'
        self.region = region
        if region == 'cn-beijing-6':
            # self.endpoint = 'https://kec.api.ksyun.com'
            self.host = 'eip.api.ksyun.com'
        else:
            self.host = 'eip.%s.api.ksyun.com' % region
        self.endpoint = 'https://' + self.host


class KSYun(object):
    class Enum:
        """
        API对象枚举
        """
        DescribeAddresses = "DescribeAddresses"
        DescribeInstances = "DescribeInstances"

    def __init__(self, api=None, *args, **kwargs):
        """
        创建金山云对象, 实例化对应的API对象
        :param api: API对象名称, 请用KSYun.Enum...方式指定
        :param args: API实例化所需要的参数列表
        :param kwargs:
        """
        if api:
            if type(api) == 'str':
                # 根据全局的对象名称获取对象实例,类似java的class.forName
                self.obj = globals()[api](*args, **kwargs)
            else:
                self.obj = api
        else:
            self.obj = None

    def load_api(self, api_obj):
        # 手动加载API对象
        self.obj = api_obj

    def sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(self, key, dateStamp, regionName, serviceName):
        kDate = self.sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = self.sign(kDate, regionName)
        kService = self.sign(kRegion, serviceName)
        ksigning = self.sign(kService, 'aws4_request')
        return ksigning

    def execute(self):
        if access_key is None or secret_key is None:
            log.error('No access key is available.')
            sys.exit()

        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')

        canonical_uri = '/'
        canonical_querystring = self.obj.request_parameters
        canonical_headers = 'host:' + self.obj.host + '\n' + 'x-amz-date:' + amzdate + '\n'
        signed_headers = 'host;x-amz-date'
        payload_hash = hashlib.sha256(''.encode("UTF-8")).hexdigest()
        canonical_request = self.obj.method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
        canonical_request = canonical_request.encode("UTF-8")
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = datestamp + '/' + self.obj.region + '/' + self.obj.service + '/' + 'aws4_request'
        string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + hashlib.sha256(
            canonical_request).hexdigest()

        signing_key = self.getSignatureKey(secret_key, datestamp, self.obj.region, self.obj.service)
        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
        headers = {'x-amz-date': amzdate, 'Authorization': authorization_header, 'Accept': 'application/json'}
        request_url = self.obj.endpoint + '?' + canonical_querystring

        try:
            r = requests.get(request_url, headers=headers, verify=False)
            log.info("fetch ksyun Success! rc: [%s] URL: [%s] with header: %s"
                     % (r.status_code, request_url, headers))
            return r.status_code, r.text
        except Exception as e:
            log.info("fetch ksyun Failed! URL: [%s] with header: %s" % (request_url, headers) + traceback.format_exc())
            raise e


@task
def get_ksyun(instance_id=None):
    """
    获取所有金山云服务器(KEC)信息
    :param instance_id: 默认实例id为空
    :return:
    """
    try:
        # 获取金山云服务器(KEC)信息
        for region in ['cn-beijing-6', 'cn-shanghai-2']:
            # di = DescribeInstances(region=region)
            # kec_res = di.execute()
            # # 分页设置
            # res = json.loads(kec_res[1])
            # if 'Error' in res:
            #     raise Exception(str(res['Error']))
            # kec_InstanceCount = json.loads(kec_res[1])['InstanceCount']  # 获取实例总数
            kec_InstanceCount = 500  # 设置实例总数
            init_num = 0  # 设置初始值
            offset = 100  # 设置步长数，page size 100条
            eip_result = DescribeAddresses(max_results=kec_InstanceCount, region=region).execute()  # 获取金山云弹性IP(EIP)信息
            while True:
                try:
                    if instance_id:
                        di = DescribeInstances(marker=init_num, max_results=offset, instance_id=instance_id, region=region)
                        kec_result = di.execute()  # 获取金山云服务器(KEC)信息

                        save_ksyun_info(kec_result, eip_result, region)
                    else:
                        di = DescribeInstances(marker=init_num, max_results=offset, region=region)
                        kec_result = di.execute()  # 获取金山云服务器(KEC)信息
                        # 保存金山云服务器信息到数据库
                        save_ksyun_info(kec_result, eip_result, region)
                    # 每次循环的最后增加步长

                    if init_num + offset > kec_InstanceCount:   # 判断，如果初始值加上步长数大于服务器实例数，则退出循环，此时已经循环完所有的实例
                        break
                    init_num += offset
                except Exception as e:
                    break

            # d_slb = DescribeSlb(region=region)
            # slb_res = json.loads(d_slb.execute()[1])
            #
            # if 'Error' in slb_res:
            #     raise Exception(str(slb_res['Error']))
            # slb_count = len(slb_res['LoadBalancerDescriptions'])
            init_num = 0  # 设置初始值
            offset = 100  # 设置步长数，page size 100条
            # print(("eip_result", eip_result))
            while True:
                if instance_id:
                    di = DescribeSlb(marker=init_num, max_results=offset, instance_id=instance_id, region=region)
                else:
                    di = DescribeSlb(marker=init_num, max_results=offset, region=region)
                kec_result = di.execute()  # 获取金山云服务器(KEC)信息
                # 保存金山云服务器信息到数据库
                save_ksyun_slb_info(kec_result, eip_result, region)
                # 每次循环的最后增加步长

                if init_num + offset > kec_InstanceCount:  # 判断，如果初始值加上步长数大于服务器实例数，则退出循环，此时已经循环完所有的实例
                    break
                init_num += offset
        log.info("crontab get kec info success!")
    except Exception as e:
        log.error("crontab get kec info error!" + traceback.format_exc())



@task
def get_ksyun_slb(instance_id=None):
    """
    获取所有金山云服务器(KEC)信息
    :param instance_id: 默认实例id为空
    :return:
    """
    try:
        # 获取金山云服务器(KEC)信息
        for region in ['cn-beijing-6', 'cn-shanghai-2']:
            di = DescribeSlb(region=region)
            slb_res = di.execute()
            # 分页设置
            res = json.loads(slb_res[1])
            if 'Error' in res:
                raise Exception(str(res['Error']))
            kec_InstanceCount = json.loads(slb_res[1])['InstanceCount']  # 获取实例总数
            init_num = 0  # 设置初始值
            offset = 100  # 设置步长数，page size 100条
            while True:
                if instance_id:
                    di = DescribeInstances(marker=init_num, max_results=offset, instance_id=instance_id, region=region)
                    kec_result = di.execute()  # 获取金山云服务器(KEC)信息
                    d = DescribeAddresses(max_results=kec_InstanceCount, region=region)
                    eip_result = d.execute()   # 获取金山云弹性IP(EIP)信息
                    # print(("eip_result", eip_result))

                    save_ksyun_info(kec_result, eip_result, region)
                else:
                    di = DescribeInstances(marker=init_num, max_results=offset, region=region)
                    kec_result = di.execute()  # 获取金山云服务器(KEC)信息
                    d = DescribeAddresses(max_results=kec_InstanceCount, region=region)
                    eip_result = d.execute()   # 获取金山云弹性IP(EIP)信息
                    # 保存金山云服务器信息到数据库
                    save_ksyun_info(kec_result, eip_result, region)
                # 每次循环的最后增加步长

                if init_num + offset > kec_InstanceCount:   # 判断，如果初始值加上步长数大于服务器实例数，则退出循环，此时已经循环完所有的实例
                    break
                init_num += offset
        log.info("crontab get kec info success!")
    except Exception as e:
        log.error("crontab get kec info error!" + traceback.format_exc())


def save_ksyun_info(kec_result, eip_result, region="cn-beijing-6"):
    """
    保存金山云信息到数据库
    :param kec_result: kec api的返回结果
    :param eip_result: eip api的返回结果
    :return:
    """
    dic_pub_ip = {}
    try:
        for eip in json.loads(eip_result[1])["AddressesSet"]:
            KsyEip.objects.insert(eip)
            if eip['State'] == 'associate' and 'NetworkInterfaceId' in eip:
                dic_pub_ip[eip['NetworkInterfaceId']] = [eip['InstanceId'], eip['PublicIp'], eip['BandWidth']]
    except Exception as e:
        log.error("get eip error！ " + traceback.format_exc())
    ksyun_RegionId = region
    # ksyun_RegionId = "cn-beijing-6"
    for kec in json.loads(kec_result[1])['InstancesSet']:  # 获取全部KEC数据
        srv_obj = ServerInfo.objects.safe_get(InstanceId=kec['InstanceId'])  # 去重复
        if not srv_obj:  # 判断如果实例id不存在，则存取数据，去重复作用
            srv_obj = ServerInfo(
                InstanceId=kec['InstanceId'],
                RegionId=ksyun_RegionId,
                ZoneId=ksyun_RegionId,
                InstanceName=kec['InstanceName'],
                InstanceType='KEC',
                InnerIpAddress=kec['NetworkInterfaceSet'][0]['PrivateIpAddress'],
                PublicIpAddress='',   # 设置每次更新初始值都为空，防止在金山云管理页面删除公网IP之后，数据库中还存在IP地址。
                Status=kec['InstanceState']['Name'],
                Cpu=kec['InstanceConfigure']['VCPU'],
                Memory=(kec['InstanceConfigure']['MemoryGb'] * 1024),
                DiskSize=kec['InstanceConfigure']['DataDiskGb'],
                DiskType=kec['InstanceConfigure']['DataDiskType'],
                server_location='ksyun', )
            srv_obj.save()
        else:   # 如果存在，就更新当前信息
            srv_obj.InstanceId = kec['InstanceId']
            srv_obj.RegionId = ksyun_RegionId
            srv_obj.ZoneId = ksyun_RegionId
            srv_obj.InstanceName = kec['InstanceName']
            srv_obj.InstanceType = 'KEC'
            srv_obj.InnerIpAddress = kec['NetworkInterfaceSet'][0]['PrivateIpAddress']
            srv_obj.Status = kec['InstanceState']['Name']
            srv_obj.Cpu = kec['InstanceConfigure']['VCPU']
            srv_obj.Memory = (kec['InstanceConfigure']['MemoryGb'] * 1024)
            srv_obj.DiskSize = kec['InstanceConfigure']['DataDiskGb']
            srv_obj.DiskType = kec['InstanceConfigure']['DataDiskType']
            srv_obj.server_location = 'ksyun'
            srv_obj.PublicIpAddress = ''  # 设置每次更新初始值都为空，防止在金山云管理页面删除公网IP之后，数据库中还存在IP地址。
            srv_obj.save()
        for k, v in list(dic_pub_ip.items()):
            if kec['NetworkInterfaceSet'][0]['NetworkInterfaceId'] == k:  # 获取EIP的公网IP等信息
                kes_info = ServerInfo.objects.filter(InstanceId=v[0])

                kes_info.update(
                    PublicIpAddress=v[1],
                    InternetMaxBandwidthOut=v[2],
                )

        # 更新组
        update_group(srv_obj)




def save_ksyun_slb_info(kec_result, eip_result, region="cn-beijing-6"):
    """
    保存金山云信息到数据库
    :param kec_result: kec api的返回结果
    :param eip_result: eip api的返回结果
    :return:
    """
    dic_pub_ip = {}
    try:
        for eip in json.loads(eip_result[1])["AddressesSet"]:
            '''
            {
                "PublicIp": "120.92.140.164",
                "AllocationId": "04915afc-84b4-4f29-b70b-7a185eeeedb8",
                "State": "associate",
                "LineId": "a2403858-2550-4612-850c-ea840fa343f9",
                "BandWidth": 50,
                "InstanceType": "Slb",
                "InstanceId": "f50e1c17-6d2d-4a8b-927c-10ac5dff76fa",
                "CreateTime": "2017-03-08 10:48:27"
            },
            '''
            if eip['State'] == 'associate' and eip['InstanceType'] == 'Slb':
                KsyEip.objects.insert(eip)
                dic_pub_ip[eip['InstanceId']] = eip
            # if eip['State'] == 'associate' and 'NetworkInterfaceId' in eip:
            #     dic_pub_ip[eip['NetworkInterfaceId']] = [eip['InstanceId'], eip['PublicIp'], eip['BandWidth']]
    except Exception as e:
        log.error("get eip error！ " + traceback.format_exc())
    # ksyun_RegionId = "cn-beijing-6"
    for kec in json.loads(kec_result[1])['LoadBalancerDescriptions']:  # 获取全部KEC数据
        srv_obj = ServerInfo.objects.safe_get(InstanceId=kec['LoadBalancerId'])  # 去重复

        if not srv_obj:  # 判断如果实例id不存在，则存取数据，去重复作用
            '''
            {
                "LoadBalancerId": "3a0bc2cf-a4e5-48da-943a-5c4a806409e3",
                "LoadBalancerName": "logstash-in",
                "Type": "internal",
                "VpcId": "10552533-3dc0-4d3e-af2d-9552ce0ed66e",
                "PublicIp": "172.31.252.130",
                "LoadBalancerState": "start",
                "CreateTime": "2016-10-12 14:26:03",
                "State": "associate"
            }
            '''
            srv_obj = ServerInfo(
                InstanceId=kec['LoadBalancerId'],
                RegionId=region,
                ZoneId=region,
                InstanceName=kec['LoadBalancerName'],
                InstanceType='SLB',
                InnerIpAddress=kec['PublicIp'] if 'PublicIp' in kec and kec['Type'] == 'internal' else '',
                PublicIpAddress=kec['PublicIp'] if 'PublicIp' in kec and kec['Type'] == 'public' else '',
                Status=kec['LoadBalancerState'],
                server_location='ksyun',
                InternetMaxBandwidthOut=dic_pub_ip[kec['LoadBalancerId']]['BandWidth'] if kec['LoadBalancerId'] in dic_pub_ip else 0,
            )
            srv_obj.save()
        else:   # 如果存在，就更新当前信息
            srv_obj.InstanceId = kec['LoadBalancerId']
            srv_obj.RegionId = region
            srv_obj.ZoneId = region
            srv_obj.InstanceName = kec['LoadBalancerName']
            srv_obj.InstanceType = 'SLB'
            srv_obj.InnerIpAddress = kec['PublicIp'] if 'PublicIp' in kec and kec['Type'] == 'internal' else ''
            srv_obj.Status = kec['LoadBalancerState']
            srv_obj.server_location = 'ksyun'
            srv_obj.PublicIpAddress = kec['PublicIp'] if 'PublicIp' in kec and kec['Type'] == 'public' else ''
            srv_obj.InternetMaxBandwidthOut = \
                dic_pub_ip[kec['LoadBalancerId']]['BandWidth'] if kec['LoadBalancerId'] in dic_pub_ip else 0
            srv_obj.save()






def update_group(server_info):
    """
    根据主机InstanceName更新所属组
    :param server_info:
    :return:
    """
    reg = re.compile('\w+-\w+-(\w+-\w+)-.*')
    match = reg.match(server_info.InstanceName)
    if match:
        group_name = match.group(1)
        sgs = ServerGroup.objects.filter(name=group_name)
        if sgs:
            sg = sgs[0]
        else:
            sg = ServerGroup(name=group_name, remark=group_name)
            sg.save()
        if not server_info.group.filter(id=sg.id):
            server_info.group.add(sg)
        sg.count = len(sg.serverinfo_set.all())
        sg.save()


def main():
    # 获取金山云列表实例
    di = DescribeInstances()
    di.execute()

    # 获取金山云弹性IP示例
    d = DescribeAddresses()
    d.execute()


if __name__ == '__main__':
    main()
