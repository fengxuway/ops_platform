# coding:utf-8
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from common.forms import PageData
from server.models import Server
from server.forms import FileForm, AddDomain
from django.conf import settings
import os
import time
import csv
from server.models import Domain
import logging
import traceback
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from common.permissions import *


log = logging.getLogger('django')


@login_required
@permission_required(VIEW_DOMAIN)
def index(request):
    log.info('Into Domain list page')
    return render(request, 'domain/index.html')


@login_required
@permission_required(VIEW_DOMAIN)
def page(request):
    log.info('searching domain data...')
    dp = PageData(request.GET)
    kw = request.GET.get("kw", "")
    area = request.GET.get("area", "")
    if dp.is_valid():
        page_info = dp.get_page_info()
        orderinfo = dp.get_sort_rule()
        kw = request.GET.get("kw", "")
        area = request.GET.get("area", "")
        ip_category = int(request.GET.get("category", 2))
        log.info('search by keyword: %s, area: %s' % (kw, area))
        try:
            datas = Domain.objects.page_search_data(
                page_info[0], page_info[1],
                orderby=orderinfo[0], order_type=orderinfo[1],
                kw=kw, area=area, ip_category=ip_category)
            data = datas[0]
            length = datas[1]

            data = [x.to_dict() for x in data]
            mp = dp.get_data(data, length)
            log.info("search Domain data success. find: %s" % length)
            return JsonResponse(mp)
        except Exception as e:
            log.error('search get the ERROR: ' + traceback.format_exc())
            return JsonResponse({'result': False, 'message': 'search get the ERROR: \n'})
    return JsonResponse({'result': False, 'message': 'the Request params probably lose something.'})


@login_required
@permission_required(perm=(ADD_DOMAIN, ), raise_exception=True)
def add(request):
    if request.method == "GET":
        log.info('Into Add Domain Page.')
        return render(request, 'domain/add.html', locals())
    else:
        log.info("start submit Add Domain Data.")
        domain_form = AddDomain(request.POST)

        if domain_form.is_valid():
            data = domain_form.cleaned_data
            try:
                _ip, _domain, _category = data['ip'], data['domain'], data['category']
                if Domain.objects.exists(_category, _ip, _domain):
                    log.error('Domain or Ip has another Map, Insert fault.')
                    message = {'result': False, 'message': '插入失败！域名或IP已经存在其他映射！',
                               'data': data}
                    return render(request, 'domain/add.html', locals())

                domain = Domain(
                    domain=_domain,
                    ip=_ip,
                    category=_category,
                    remark=data['remark']
                )
                domain.save()
                server_update(_category, _ip, _domain)
                log.info("Domain-ip saved success!")
                message = {'result': True, 'message': '域名-IP映射添加成功！', 'title': '添加域名-IP结果'}
                return render(request, 'domain/add-result.html', locals())
            except Exception as e:
                log.error('Insert Domain get the ERROR: ' + traceback.format_exc())
                message = {'result': False, 'message': '服务器发生异常：' + e.message + " 请稍候重试！", 'data': data}
                return render(request, 'domain/add.html', locals())
        else:
            message = {'result': False, 'message': '表单验证失败！请检查您的填写。'}
            return render(request, 'domain/add.html', locals())


@login_required
@permission_required(perm=(CHANGE_DOMAIN,), raise_exception=True)
def update(request, dmn_id):
    """
    modify Domain by id
    :param request:
    :param dmn_id: domain id
    :return:
    """
    if request.method == "GET":
        log.info('Into Update domain page.')
        dmns = Domain.objects.filter(id=dmn_id)
        if dmns:
            dmn = dmns[0]
            log.info("search success and prepage update Domain: " + str(dmn))
            return render(request, 'domain/add.html', {"domain": dmn})
        else:
            log.error("search Domain<%s> error and turn to Add Domain page." % dmn_id)
            return render(request, 'domain/add.html', {"domain": None})
    else:
        doman_form = AddDomain(request.POST)

        if doman_form.is_valid():
            data = doman_form.cleaned_data
            dmn = Domain.objects.filter(id=dmn_id)
            dmn.update(
                domain=data['domain'],
                ip=data['ip'],
                category=data['category'],
                remark=data['remark']
            )
            # update Server domain reference
            server_update(data['category'], data['ip'], data['domain'])
            message = {'result': True, 'message': 'Domain修改成功！', 'title': '更新Domain结果'}
            return render(request, 'domain/add-result.html', locals())
        else:
            message = {'result': False, 'message': '表单验证失败！请检查您的填写。'}
            return render(request, 'domain/add.html', locals())


def server_update(category, ip, domain):
    """
    域名修改和添加后，Server要及时更新
    :param category:
    :param ip:
    :param domain:
    :return:
    """
    log.info("Server %s IP update domain to '%s'" % ('Inner' if category == 0 else 'Outer', domain))
    if category == 0:
        # inner IP
        Server.objects.filter(inner_ip=ip).update(domain=domain)
    else:
        # outer IP
        Server.objects.filter(outer_ip=ip).update(domain=domain)


@login_required
@permission_required(perm=(CHANGE_DOMAIN, ), raise_exception=True)
def upload(request):
    if request.method == "GET":
        log.info("Into Domain CSV upload page")
        return render(request, 'domain/upload.html', locals())

    log.info("start upload Domain CSV file and analyze save to Database")
    uf = FileForm(request.POST, request.FILES)
    table_header = [
        '域名', 'IP地址', 'IP类型', '备注'
    ]
    if uf.is_valid():
        upload_file = uf.cleaned_data['upload_file']
        if upload_file.name.lower().endswith('.csv'):
            saved_path = os.path.join(settings.UPLOAD_URL, 'domain_template')
            if not os.path.exists(saved_path):
                os.makedirs(saved_path)
            saved_file = os.path.join(saved_path, str(time.time()) + '.csv')
            with open(saved_file, 'wb') as f:
                f.write(upload_file.read())
            log.info("file saved in: " + saved_file)
            data = csv.reader(open(saved_file, 'rb'))

            i = 0  # 行计数器
            not_add = []    # 未添加列表
            added_count = 0     # 已添加数量
            for row in data:
                row = [x.decode("GBK") for x in row]
                i += 1
                if i == 1:
                    csv_header = row
                    diff = set(table_header) - set(csv_header)
                    if diff:
                        missing_header = ','.join(diff)
                        log.error("CSV file's table header not Support. Missing: " + missing_header)
                        return JsonResponse({'result': False, 'message': '表头信息不符！缺少表头：' + missing_header})
                    continue

                category = 0 if row[csv_header.index('IP类型')].find('内') >= 0 else 1
                _domain = row[csv_header.index('域名')]
                _ip = row[csv_header.index('IP地址')]
                if Domain.objects.exists(category, _ip, _domain):
                    not_add.append({'domain': _domain, 'ip': _ip})
                    continue
                Domain(
                    domain=_domain,
                    ip=_ip,
                    category=category,
                    remark=row[csv_header.index('备注')]
                ).save()
                added_count += 1
                server_update(category, _ip, _domain)
            message = {'result': True, 'message': '文件上传成功！', 'not_add': not_add, 'added': added_count}
            log.info("file upload success and save to database.")
        else:
            log.error("file upload success But File Format not Support!")
            message = {'result': False, 'message': '文件上传失败！仅支持CSV格式'}
    else:
        log.error('no file found.')
        message = {'result': False, 'message': '请先选择文件上传'}
    log.info("upload result: " + str(message))
    return JsonResponse(message)


@login_required
@permission_required(perm=(DELETE_DOMAIN,), raise_exception=True)
def remove(request):
    domain_id = request.POST.getlist("id[]", [])
    log.info("start Remove Domain: " + str(domain_id))
    if not domain_id:
        log.error("Remove Domain not appoint!")
        return JsonResponse({'result': False, 'message': '请输入要删除的Domain ID'})

    try:
        srv = Domain.objects.filter(id__in=domain_id)
        for i in srv:
            if i.category == 0:
                Server.objects.filter(inner_ip=i.ip).update(domain='')
            else:
                Server.objects.filter(outer_ip=i.ip).update(domain='')
        srv.delete()
        log.info('Domain delete Sucess！' + str(domain_id))
        return JsonResponse({'result': True, 'message': ''})
    except Exception as e:
        log.error("Domain Remove Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '删除失败：' + e.message})
