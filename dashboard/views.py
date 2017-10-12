#!/usr/bin/env python
# coding=utf-8

from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from dashboard.models import SiteRecord
import traceback
import time
import pytz
import json

@csrf_exempt
def add(request):
    try:
        data = request.POST.get("data")
        last_time = request.POST.get("time")
        hostname = request.POST.get("hostname")
        date = datetime.strptime(last_time, '%Y%m%d%H%M')
        other_rows = SiteRecord.objects.filter(last_time=date).exclude(hostname=hostname).exclude(hostname='merge')
        if other_rows:
            other_row = other_rows[0]
            data_obj1 = json.loads(data)
            data_obj0 = json.loads(other_row.data)
            data_map = {}
            for i, j in data_obj1 + data_obj0:
                data_map.setdefault(i, 0)
                data_map[i] += j
            data_merge = sorted(iter(data_map.items()), key=lambda d: d[1], reverse=True)[0:20]
            SiteRecord(data=json.dumps(data_merge), last_time=date, hostname='merge').save()

        if not SiteRecord.objects.filter(last_time=date, hostname=hostname):
            SiteRecord(data=data, last_time=date, hostname=hostname).save()
    except ValueError:
        print("time format error")
        traceback.print_exc()
    except Exception:
        traceback.print_exc()
    return JsonResponse({'success': True})


def read(request):
    records = SiteRecord.objects.filter(hostname='merge').order_by('-update_time')[0:1]
    if records:
        record = records[0]
        last_time = record.last_time
    else:
        return JsonResponse({'result': False, 'message': 'No log record found!'})

    data_ls = json.loads(record.data)
    last_time = last_time.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(settings.TIME_ZONE))
    last_time_str = last_time.strftime('%Y-%m-%d %H:%M')
    header = []
    data = []
    for i, j in data_ls[0:10]:
        header.append(i)
        data.append(j)
    return JsonResponse({"result": True, "header": header, "data": data, "time": last_time_str})

