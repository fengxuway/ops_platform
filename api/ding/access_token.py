#!/usr/bin/env python
# coding:utf-8
import requests
import json, os
from celery.task import task


CorpID = '__CorpID__'
CorpSecret = '__CorpSecret__'

url = 'https://oapi.dingtalk.com/gettoken?corpid=%s&corpsecret=%s' % (CorpID, CorpSecret)

print(os.getcwd())
def write_token(ACCESS_TOKEN):
    """
    写入access_token到文件中
    :param ACCESS_TOKEN:
    :return:
    """
    with open(".access_token", 'w') as f:
        f.write(ACCESS_TOKEN)


def request_access_token():
    """
    请求钉钉服务器获取access_token
    :return:
    """
    ACCESS_TOKEN = None
    response = requests.get(url, verify=False)
    content = json.loads(response.text)
    if content['errcode'] == 0:
        ACCESS_TOKEN = content['access_token']
        write_token(ACCESS_TOKEN)
    return ACCESS_TOKEN


def get_token():
    from django.conf import settings
    """
    从文件中读取token。如果不存在该文件,则发送请求获取
    :return:
    """
    try:
        with open(settings.BASE_DIR + "/.access_token", 'r') as f:
            ACCESS_TOKEN = f.read()
        return ACCESS_TOKEN
    except IOError as e:
        return request_access_token()


@task
def main():
    request_access_token()


if __name__ == '__main__':
    main()
