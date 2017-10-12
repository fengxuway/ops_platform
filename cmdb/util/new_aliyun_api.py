#!/usr/bin/env python
# coding:utf-8

import base64
import hmac
from hashlib import sha1
import urllib
import time
import json
import uuid
from urllib.parse import quote, urlencode
import requests

ALIYUN_ACCESS_KEY_ID = "__ALIYUN_ACCESS_KEY_ID__"
ALIYUN_ACCESS_KEY_SECRET = "__ALIYUN_ACCESS_KEY_SECRET__"


class AliyunMonitor(object):
    def __init__(self, url):
        self.access_id = ALIYUN_ACCESS_KEY_ID
        self.access_secret = ALIYUN_ACCESS_KEY_SECRET
        self.url = url
        self.version = '2014-05-26'
        if 'slb.aliyuncs.com' in self.url:
            self.version = '2014-05-15'

    def sign(self, accessKeySecret, parameters):
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])
        canonicalizedQueryString = ''

        for (k, v) in sortedParameters:
            canonicalizedQueryString += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)

        stringToSign = 'GET&%2F&' + self.percent_encode(canonicalizedQueryString[1:])    # 使用get请求方法
        key = bytes(accessKeySecret + "&", 'UTF-8')
        message = bytes(stringToSign, 'UTF-8')
        # h = hmac.new(accessKeySecret + "&", stringToSign, sha1)
        # signature = base64.encodestring(h.digest()).strip()

        digester = hmac.new(key, message, sha1)
        signature1 = digester.digest()
        signature2 = base64.urlsafe_b64encode(signature1).strip()
        return signature2

    def percent_encode(self, encodeStr):
        encodeStr = str(encodeStr)
        # 下面这行挺坑的，使用上面文章中的方法会在某些情况下报错，后面详细说明
        res = quote(encodeStr.encode('utf-8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        res = res.replace('%7E', '~')
        return res

    def _make_url(self, params):
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        parameters = {
            'Format': 'JSON',
            'Version': self.version,
            'AccessKeyId': self.access_id,
            'SignatureVersion': '1.0',
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureNonce': str(uuid.uuid1()),
            'Timestamp': timestamp,
        }
        for key in params.keys():
            parameters[key] = params[key]

        signature = self.sign(self.access_secret, parameters)
        parameters['Signature'] = signature
        ss = str(signature)
        if '-' in ss or '_' in ss:
            raise Exception()

        # return parameters
        url = self.url + "/?" + urlencode(parameters)
        return url

    def make_url(self, **params):
        for i in range(0, 50):
            try:
                return self._make_url(params)
            except Exception as e:
                continue
        raise Exception("Aliyun URL gen ERROR!")


class Aliyun_api(object):
    """
    获取磁盘信息
    """
    def __init__(self, region_id='cn-beijing', baseurl='https://ecs.aliyuncs.com'):
        self.api = AliyunMonitor(baseurl)
        self.RegionId = region_id

    # DescribeRegions 查询查询可用地域列表
    def describe_regions_request(self):
        """
        DescribeRegions 查询所有地域
        :return:
        """
        url = self.api.make_url(Action="DescribeRegions", RegionId=self.RegionId)
        # res = requests.get(url)
        # return str(res.content, 'utf-8')
        return url

    # DescribeInstances 查询所有实例的详细信息
    def describe_instances_request(self, instance_ids=None, page_number=1, page_size=100):
        if not instance_ids:
            url = self.api.make_url(Action="DescribeInstances",
                                     PageSize=page_size,
                                     PageNumber=page_number,
                                     RegionId=self.RegionId)
        else:
            url = self.api.make_url(Action="DescribeInstances",
                                    InstanceIds=json.dumps(instance_ids),
                                    PageSize=page_size,
                                    PageNumber=page_number,
                                    RegionId=self.RegionId)
        # res = requests.get(url)
        # return str(res.content, 'utf-8')
        return url

    # DescribeDisks 查询磁盘信息
    def describe_disks_request(self, page_number=1, page_size=100):
        url = self.api.make_url(Action="DescribeDisks",
                                 PageSize=page_size,
                                 PageNumber=page_number,
                                 RegionId=self.RegionId)
        # res = requests.get(url)
        # return str(res.content, 'utf-8')
        return url

    def describe_load_balancers_request(self):
        return self.api.make_url(Action='DescribeLoadBalancers',
                                RegionId=self.RegionId)


    def do_action(self, url):
        res = requests.get(url)
        return str(res.content, 'utf-8')


def main():
    aa = Aliyun_api(region_id='cn-shanghai')
    u = aa.describe_instances_request()
    print(aa.do_action(u))


if __name__ == '__main__':
    main()
