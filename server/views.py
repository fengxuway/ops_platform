# coding:utf-8
import csv
import logging
import os
import traceback
import subprocess
import datetime

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import ObjectDoesNotExist

from common.util import des
from common.views import page_handler
from options.models import DataOption
from server.forms import FileForm, AddServer
from server.models import Server
from cmdb.models import ServerInfo
from server.logic import connect_server
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from common.permissions import *


log = logging.getLogger('django')


@login_required
@permission_required(VIEW_SERVER)
def index(request):
    log.info('Into Server list page')
    kw = request.GET.get('kw', '')
    return render(request, 'server/index.html', locals())


@login_required
@permission_required(VIEW_SERVER)
@page_handler
def page(request):
    kw = request.GET.get("kw", "")
    area = request.GET.get("area", "")
    log.info('search by keyword: %s, area: %s' % (kw, area))
    query = Server.objects.all()
    if kw:
        query = query.filter(Q(name__icontains=kw) | Q(hostname__icontains=kw) | Q(inner_ip__contains=kw) |
                             Q(outer_ip__contains=kw) | Q(domain__icontains=kw) |
                             Q(area__icontains=kw) | Q(server_id__icontains=kw))
    if area:
        query = query.filter(area__icontains=area)
    return query


@login_required
@permission_required(VIEW_SERVER)
@page_handler
def page_enabled(request):
    kw = request.GET.get("sSearch", "")
    query = ServerInfo.objects.all()
    if kw:
        query = query.filter(Q(name__icontains=kw) | Q(hostname__icontains=kw) | Q(inner_ip__contains=kw) |
                             Q(outer_ip__contains=kw) | Q(domain__icontains=kw) |
                             Q(area__icontains=kw) | Q(server_id__icontains=kw))
    return query


@login_required
@permission_required(perm=(ADD_SERVER,), raise_exception=True)
def add(request):
    if request.method == "GET":
        server_form = AddServer()
        log.info('Into Add Server Page.')
        return render(request, 'server/add.html', locals())
    else:
        log.info("start submit Add Server Data.")
        server_form = AddServer(request.POST)

        if server_form.is_valid():
            try:
                data = server_form.cleaned_data
                srv = Server(
                    name=data['name'],
                    inner_ip=data['inner_ip'],
                    outer_ip=data['outer_ip'],
                    area=data['area'],
                    user=data['user'],
                    password=data['password'],
                    port=data['port'],
                    bandwidth=data['bandwidth'],
                    monitor=data['monitor'],
                    remark=data['remark']
                )
                if srv.insert(enc=True):
                    # 更新数据字典，增加机房（如果不存在）
                    DataOption(
                        category='area',
                        keyword=data['area']
                    ).insert()
                    # 连接到主机，拷贝公钥
                    connect_server.delay(srv.id)

                log.info("Insert Server data success!")
                message = {'result': True, 'message': 'Server添加成功！', 'title': '添加Serve结果'}
                return render(request, 'server/add-result.html', locals())
            except Exception as e:
                log.error('Insert Server get the ERROR: ' + traceback.format_exc())
                message = {'result': False, 'message': '服务器发生异常：'+e.message + " 请稍候重试！"}
                return render(request, 'server/add.html', locals())
        else:
            log.error("表单验证失败! " + str(server_form.errors))
            message = {'result': False, 'message': '表单验证失败！请检查您的填写。' + str(server_form.errors)}
            return render(request, 'server/add.html', locals())


@login_required
@permission_required(perm=(CHANGE_SERVER,), raise_exception=True)
def update(request, srv_id):
    """
    modify Server by id
    :param request:
    :param srv_id: server id
    :return:
    """
    if request.method == "GET":
        log.info('Into Update server page.')
        srvs = Server.objects.filter(id=srv_id)
        if srvs:
            srv = srvs[0]
            log.info("search success and prepage update Server: " + str(srv))
            return render(request, 'server/add.html', {"srv": srv})
        else:
            log.error("search Server<%s> error and turn to Add Server page." % srv_id)
            return render(request, 'server/add.html', {"srv": None})
    else:
        server_form = AddServer(request.POST)

        if server_form.is_valid():
            data = server_form.cleaned_data
            srv = Server.objects.filter(id=srv_id)
            srv.update(
                name=data['name'],
                inner_ip=data['inner_ip'],
                outer_ip=data['outer_ip'],
                area=data['area'],
                user=data['user'],
                password=des.encrypt(data['password']),
                bandwidth=data['bandwidth'],
                monitor=data['monitor'],
                remark=data['remark']
            )
            # 更新数据字典，增加机房（如果不存在）
            DataOption(
                category='area',
                keyword=data['area']
            ).insert()
            message = {'result': True, 'message': 'Server修改成功！', 'title': '更新Serve结果'}
            return render(request, 'server/add-result.html', locals())
        else:
            message = {'result': False, 'message': '表单验证失败！请检查您的填写。'}
            return render(request, 'server/add.html', locals())


@login_required
@permission_required(perm=(CHANGE_SERVER,), raise_exception=True)
def upload(request):
    if request.method == "GET":
        uf = FileForm()
        log.info("Into Server CSV upload page.")
        return render(request, 'server/upload.html', locals())

    log.info("CSV file uploaded and analyze...")
    uf = FileForm(request.POST, request.FILES)
    table_header = [
        '主机名', '内网IP', '外网IP', '用户名', '密码', '端口', '机房', '机架', '带宽', '监控', '备注'
        ]

    message = {}
    if uf.is_valid():
        upload_file = uf.cleaned_data['upload_file']
        if upload_file.name.lower().endswith('.csv'):
            saved_path = os.path.join(settings.UPLOAD_URL, 'server_template')
            if not os.path.exists(saved_path):
                os.makedirs(saved_path)
            now = datetime.datetime.now()
            saved_file = os.path.join(saved_path, now.strftime('%Y%m%d%H%M%S_%f') + '.csv')
            with open(saved_file, 'wb') as f:
                f.write(upload_file.read())
            log.info("file saved in: " + saved_file)
            try:
                data = csv.reader(open(saved_file, 'rb'))

                i = 0
                # 添加数量和未添加server列表
                added_count = 0
                ignore_list = []
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

                    srv = Server(
                        name=row[csv_header.index('主机名')],
                        inner_ip=row[csv_header.index('内网IP')],
                        outer_ip=row[csv_header.index('外网IP')],
                        # domain=row[csv_header.index(u'域名')],
                        area=row[csv_header.index('机房')],
                        rack=row[csv_header.index('机架')],
                        user=row[csv_header.index('用户名')],
                        password=row[csv_header.index('密码')],
                        port=row[csv_header.index('端口')],
                        bandwidth=row[csv_header.index('带宽')],
                        monitor=row[csv_header.index('监控')],
                        remark=row[csv_header.index('备注')]
                    )
                    if srv.insert(enc=True):
                        # 更新数据字典，增加机房（如果不存在）
                        DataOption(
                            category='area',
                            keyword=row[csv_header.index('机房')]
                        ).insert()
                        added_count += 1
                        # 连接到主机，拷贝公钥
                        connect_server.delay(srv.id)
                    else:
                        ignore_list.append(srv.to_dict())

                message = {'result': True, 'message': '文件上传成功！',
                           'added_count': added_count, 'ignore_list': ignore_list}
                log.info("file upload success and save to database.")
            except Exception:
                traceback.print_exc()
        else:
            log.error("file upload success But File Format not Support!")
            message = {'result': False, 'message': '文件上传失败！仅支持CSV格式'}
    else:
        message = {'result': False, 'message': '请先选择文件上传'}
        log.error('no file found.')
    log.info("upload result: " + str(message))
    return JsonResponse(message)


@login_required
@permission_required(perm=(DELETE_SERVER,), raise_exception=True)
def remove_server(request):
    srv_id = request.POST.getlist("id[]", [])
    log.info("start Remove Server: " + str(srv_id))
    if not srv_id:
        log.error("Remove Server not appoint!")
        return JsonResponse({'result': False, 'message': '请输入要删除的Server ID'})

    try:
        srv = Server.objects.filter(id__in=srv_id)
        srv.delete()
        log.info('Server delete Sucess！' + str(srv_id))
        return JsonResponse({'result': True, 'message': ''})
    except Exception as e:
        log.error("Server Remove Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '删除失败：' + e.message})


@login_required
def search_by_area(request):
    area = request.POST.get("area", '')
    if area:
        srvs = Server.objects.filter(area__icontains=area)
        srvs = [srv.to_dict() for srv in srvs]
        return JsonResponse(srvs, safe=False)
    return JsonResponse({'result': False, 'message': 'request missing param named "area"!'})


@login_required
@permission_required(VIEW_SERVER)
def view_log(request, srv_id):
    log.info("reading the Server<%s>'s connect logs..." % srv_id)
    try:
        srv = Server.objects.get(id=srv_id)
        return JsonResponse({'result': True, 'message': srv.connect_log})
    except ObjectDoesNotExist:
        log.error("Log get error, not find this Server<%s>." % srv_id)
        return JsonResponse({'result': False, 'message': '该Server不存在'})


@login_required
@permission_required(perm=(CHANGE_SERVER, ), raise_exception=True)
def connect(request, srv_id):
    log.info("Connect again to the Server<%s>..." % srv_id)
    try:
        result = connect_server(srv_id)
        srv = Server.objects.get(id=srv_id)
        return JsonResponse({'result': result, 'message': srv.connect_log})
    except ObjectDoesNotExist:
        log.error("Log get error, not find this Server<%s>." % srv_id)
        return JsonResponse({'result': False, 'message': '该Server不存在'})
