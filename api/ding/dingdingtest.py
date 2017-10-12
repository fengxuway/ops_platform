#!/usr/bin/env python
# coding:utf8

import requests
import json
import random
import logging
from api.ding.access_token import get_token


log = logging.getLogger('django')

# url = 'https://oapi.dingtalk.com/chat/send?access_token=%s' % "f238c6e4e43a3541bc0eb1bda194532f"
url = 'https://oapi.dingtalk.com/chat/send?access_token=%s' % get_token()
headers = {'Content-Type': 'application/json'}


def get_oa_message(region, num, kpi_list, detail_url, kpi_hour, debug):
    chatid = "chat99b654053ac0890abb1e83c7028f84f6" if debug else "chat5ee4833e2a7f19a5485ac6fcf6b903ab"
    kpi_form = [{
        "key": "站点列表",
        "value": ""
    }]
    for i in range(len(kpi_list)):
        kpi_form.append({
            "key": "%d. " % (i + 1),
            "value": kpi_list[i]
        })

    emojis = {
        "ok": ["✌️", "👌", "🆗", "💋"],
        "error": ["💀", "🆘", "😱", "🔥"]
    }

    if num == 0:
        rnd_idx = random.randint(0, len(emojis['ok']) - 1)
        emoji = emojis['ok'][rnd_idx]
    else:
        rnd_idx = random.randint(0, len(emojis['error']) - 1)
        emoji = emojis['error'][rnd_idx]

    title = "【%s】%s:00-%s:00的 KPI %d 个站点数据异常!" % (region, kpi_hour, kpi_hour+1, num) \
        if num > 0 else "【%s】%s:00-%s:00的 KPI 站点数据正常" % (region, kpi_hour, kpi_hour+1)
    return {
        "chatid": chatid,
        "sender": "Xiaoneng_Alert",
        "msgtype": "oa",
        "oa": {
            "message_url": detail_url,
            "pc_message_url": detail_url,
            "head": {
                "bgcolor": "ffbb0000" if num > 0 else "ff00bb00",
                "text": "ERROR" if num > 0 else "OK"
            },
            "body": {
                # "title": "KPI %d 个站点数据异常!" % num if num > 0 else "KPI 站点数据正常!",
                # "title": "【%s】%s:00-%s:00的 KPI %d 个站点数据异常!" % (region, kpi_hour, kpi_hour+1, num) if num > 0 else "%s:00的 KPI 站点数据正常!" % kpi_hour,
                "title": title,
                "form": kpi_form if num > 0 else [],
                "rich": {
                    "num": emoji,
                    "unit": ""
                },
                # "content": content,
                "image": "",
                "filecount": "",
                "author": "小能Dragonfly报警中心"
            }
        }
    }


def send_ding(region, num, kpi_list, detail_url, kpi_hour, debug=True):
    data = get_oa_message(region, num, kpi_list, detail_url, kpi_hour, debug)
    log.info("Prepare send Dingding...Data: ")
    log.info(data)
    log.info("URL: " + url)
    response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    log.info("response: ")
    log.info(response)
    log.info("=================================")
    return response.text


def main():
    # response = requests.post(url, data=json.dumps(data_error), headers=headers)
    # print(response.text)
    send_ding('Aliyun', 10, ['1', '2', '3'], 'https://www.baidu.com/s?wd=中文', kpi_hour=7)

if __name__ == '__main__':
    main()
