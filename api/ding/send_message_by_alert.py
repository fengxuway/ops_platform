#!/usr/bin/env python
# coding:utf8

import requests
import json
from api.ding.access_token import get_token
import random
from django.conf import settings


url = 'https://oapi.dingtalk.com/chat/send?access_token=%s' % get_token()

headers = {'Content-Type': 'application/json'}


def get_oa_message(num, kpi_list, detail_url, kpi_hour, debug):
    chatid = "chat4cab437cc17cbf934b5e5ed699855f39" if debug else "chat5ee4833e2a7f19a5485ac6fcf6b903ab"
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
                "title": "%s:00的 KPI %d 个站点数据异常!" % (kpi_hour, num) if num > 0 else "%s:00的 KPI 站点数据正常!" % kpi_hour,
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


def send_ding(num, kpi_list, detail_url, kpi_hour, debug=settings.DEBUG):
    data = get_oa_message(num, kpi_list, detail_url, kpi_hour, debug)
    response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
    return response.text


def main():
    # response = requests.post(url, data=json.dumps(data_error), headers=headers)
    # print(response.text)
    pass

if __name__ == '__main__':
    main()
