# coding:utf-8
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Create your views here.
from cmdb.models import ServerInfo
from django.db.models import Q
import jinja2
import os
from datetime import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import traceback
# from api.ding.send_message_by_alert import send_ding
import logging
import json
from api.ding.dingdingtest import send_ding

log = logging.getLogger('django')


def ip_to_hostname(request, ip=''):
    """
    根据IP获取主机名
    :param request:
    :param ip:
    :return:
    """
    if ip:
        si = ServerInfo.objects.filter(Q(PublicIpAddress=ip) | Q(InnerIpAddress=ip))
        if si:
            return HttpResponse(si[0].InstanceName)
    return HttpResponse("Not found Server with IP [%s]" % ip)


@csrf_exempt
def kpi_ding(request):
    print(request)
    if request.POST:
        num = request.POST.get("num", '')
        kpi_list_str = request.POST.get("list", "")
        content = request.POST.get("content", "")
        time_hour = request.POST.get("time", 0)
        region = request.POST.get("region", '-')
    elif request.body:
        print(request.body.decode())
        data = json.loads(request.body.decode())
        kpi_list_str, content = data['list'], data['content']
        num = data.get("num", '')
        time_hour = data.get("time", 0)
        region = data.get("region", '-')
    else:
        return HttpResponse("Error! Please POST request!")
    debug = request.GET.get("debug", '')
    if debug:
        if debug == 'true':
            debug = True
        else:
            debug = False
    else:
        debug = settings.DEBUG
    time_hour = int(time_hour)
    now = datetime.now()
    ym = now.strftime("%Y%m")
    mdh = now.strftime("%m%d-%H%M%S")

    template_name = "%s/%s-kpi-%s.html" % (ym, region, mdh)
    template_dir = settings.BASE_DIR + '/static/monitor/kpi/%s' % ym
    kpi_list = sorted([i for i in kpi_list_str.split(',') if i != ''] if kpi_list_str else [])
    try:
        num = int(num)
    except ValueError as ve:
        num = len(kpi_list)

    try:
        print(settings.BASE_DIR + '/templates/api/kpi-template.html')
        with open(settings.BASE_DIR + '/templates/api/kpi-template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        template = jinja2.Template(template_content)
        cols = 2
        if num / 3.0 > 7:
            cols = 4
        elif num / 2.0 > 6:
            cols = 3
        rendered_kpi = template.render({
            'cols': cols,
            'num': num,
            'kpi_list': kpi_list,
            'content': content,
            'region': region
        })
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        with open(settings.BASE_DIR + '/static/monitor/kpi/%s' % template_name, 'w', encoding='utf-8') as f:
            f.write(rendered_kpi)
        callback_url = settings.BASE_URL + "/static/monitor/kpi/%s" % template_name

        log.info("Dingding URL: " + str(callback_url))

        send_ding(region, num, kpi_list, callback_url, time_hour, debug=debug)
        return HttpResponse('Dingding Send Success: %s' % callback_url)
    except Exception as e:
        traceback.print_exc()
        log.error(traceback.format_exc())
        return HttpResponse('Dingding Send Error: %s' % traceback.format_exc())

