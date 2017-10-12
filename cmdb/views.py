#!/usr/bin/env python
# coding=utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404, HttpResponse
from cmdb.models import ServerInfo, ServerGroup, KsyEip
from common.views import page_handler
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import logging
from cmdb.logic import update_server_info, get_ali_servers, get_ali_disk_info, get_ksyun
import traceback
import datetime
from service.logic import run_task
from .forms import AddServer, AddServerApiForm
from server.logic import connect_server
from options.models import DataOption
from common.util import des
from common.util.shell_util import ssh_copy_id_passwd
from django.views.decorators.csrf import csrf_exempt
from common.util.des import decrypt, encrypt
from common.util.id_creater import random_str
from common.util.ansible_api import Runner
from common.util.ansible_api import ResultsCollector


log = logging.getLogger('django')


@login_required
@page_handler
def job_list_page(request):
    kw = request.GET.get("kw", "")
    sSearch = request.GET.get("sSearch", "")
    if not kw:
        kw = sSearch
    kw = kw.strip()
    search_type = request.GET.get("search_type", "")
    query = ServerInfo.objects.all().filter(enabled=0,
                                            update_time__gt=datetime.datetime.utcnow() - datetime.timedelta(hours=64))
    log.info("page: " + kw)
    # 搜索阿里云或金山云
    if search_type == 'aliyun-slb':
        query = query.filter(InstanceType='SLB', server_location='aliyun')
    elif search_type == 'aliyun-ecs':
        query = query.filter(InstanceType='ECS', server_location='aliyun')
    elif search_type == 'ksyun-ecs':
        query = query.filter(InstanceType='KEC', server_location='ksyun')
    elif search_type == 'ksyun-slb':
        query = query.filter(InstanceType='SLB', server_location='ksyun')

    if kw:
        # 分组查询, 如果未选择查询类别
        if not search_type or search_type in ['aliyun-ecs', 'aliyun-slb', 'ksyun-ecs', 'ksyun-slb']:
            query = query.filter(Q(InstanceName__icontains=kw) | Q(InnerIpAddress__icontains=kw) |
                                 Q(PublicIpAddress__icontains=kw) | Q(RegionId__icontains=kw) | Q(ZoneId__icontains=kw))
        else:
            # 搜索主机名
            if search_type == 'hostname':
                query = query.filter(Q(InstanceName__icontains=kw))
            # 搜索分组
            elif search_type == 'group':
                sgs = ServerGroup.objects.filter(name__iexact=kw)
                if sgs:
                    sg = sgs[0]
                    query = sg.serverinfo_set.all()
                else:
                    query = query.filter(id=0)
            # 搜索IP地址
            elif search_type == 'ipaddr':
                query = query.filter(Q(InnerIpAddress__contains=kw) | Q(PublicIpAddress__contains=kw))
            # 搜索区域
            elif search_type == 'region':
                query = query.filter(Q(RegionId__icontains=kw) | Q(ZoneId__icontains=kw))
    return query

@login_required
@page_handler
def job_list_page_phone(request):
    kw = request.GET.get("kw", "")
    sSearch = request.GET.get("sSearch", "")
    if not kw:
        kw = sSearch
    kw = kw.strip()
    search_type = request.GET.get("search_type", "")
    query = ServerInfo.objects.all().filter(enabled=0, update_time__gt=datetime.datetime.utcnow() - datetime.timedelta(hours=64)).filter(Q(InstanceType='ECS') | Q(InstanceType='KEC'))
    log.info("page_phone: " + kw)
    if kw:
        # 分组查询, 如果未选择查询类别
        if not search_type or search_type in ['aliyun-ecs', 'aliyun-slb', 'ksyun-ecs', 'ksyun-slb']:
            query = query.filter(Q(InstanceName__icontains=kw) | Q(InnerIpAddress__icontains=kw) |
                                 Q(PublicIpAddress__icontains=kw) | Q(RegionId__icontains=kw) | Q(ZoneId__icontains=kw))
        else:
            # 搜索主机名
            if search_type == 'hostname':
                query = query.filter(Q(InstanceName__icontains=kw))
            # 搜索分组
            elif search_type == 'group':
                sgs = ServerGroup.objects.filter(name__iexact=kw)
                if sgs:
                    sg = sgs[0]
                    query = sg.serverinfo_set.all()
                else:
                    query = query.filter(id=0)
            # 搜索IP地址
            elif search_type == 'ipaddr':
                query = query.filter(Q(InnerIpAddress__contains=kw) | Q(PublicIpAddress__contains=kw))
            # 搜索区域
            elif search_type == 'region':
                query = query.filter(Q(RegionId__icontains=kw) | Q(ZoneId__icontains=kw))
    return query

@login_required
@page_handler
def eip_page(request):
    kw = request.GET.get("kw", "")
    sSearch = request.GET.get("sSearch", "")
    if not kw:
        kw = sSearch
    kw = kw.strip()
    search_type = request.GET.get("search_type", "")
    query = KsyEip.objects.all().filter(update_time__gt=datetime.datetime.utcnow() - datetime.timedelta(hours=9))
    if search_type:
        if search_type == 'KEC':
            query = query.filter(InstanceType='Ipfwd')
        else:
            query = query.filter(InstanceType='Slb')
    if kw:
        query = query.filter(PublicIp__icontains=kw)

    query = query.order_by('PublicIp')
    return query



@login_required
def export(request):
    kw = request.GET.get("kw", "")
    sSearch = request.GET.get("sSearch", "")
    if not kw:
        kw = sSearch
    kw = kw.strip()
    search_type = request.GET.get("search_type", "")
    query = ServerInfo.objects.all().filter(enabled=0,
                                            update_time__gt=datetime.datetime.utcnow() - datetime.timedelta(hours=64))
    # 搜索阿里云或金山云
    if search_type in ['aliyun', 'ksyun']:
        query = query.filter(Q(server_location=search_type))
    elif search_type == 'aliyun-slb':
        query = query.filter(Q(InstanceType='SLB'))
    elif search_type == 'aliyun-ecs':
        query = query.filter(Q(InstanceType='ECS'))

    if kw:
        # 分组查询, 如果未选择查询类别
        if not search_type or search_type in ['aliyun', 'aliyun-slb', 'ksyun']:
            query = query.filter(Q(InstanceName__icontains=kw) | Q(InnerIpAddress__icontains=kw) |
                                 Q(PublicIpAddress__icontains=kw) | Q(RegionId__icontains=kw) | Q(ZoneId__icontains=kw))
        else:
            # 搜索主机名
            if search_type == 'hostname':
                query = query.filter(Q(InstanceName__icontains=kw))
            # 搜索分组
            elif search_type == 'group':
                sgs = ServerGroup.objects.filter(name__iexact=kw)
                if sgs:
                    sg = sgs[0]
                    query = sg.serverinfo_set.all()
                else:
                    query = query.filter(id=0)
            # 搜索IP地址
            elif search_type == 'ipaddr':
                query = query.filter(Q(InnerIpAddress__contains=kw) | Q(PublicIpAddress__contains=kw))
            # 搜索区域
            elif search_type == 'region':
                query = query.filter(Q(RegionId__icontains=kw) | Q(ZoneId__icontains=kw))
    result = ""
    for si in query:
        x = si.to_dict()
        result += "%-30s&nbsp;&nbsp;&nbsp;&nbsp;%15s&nbsp;&nbsp;&nbsp;&nbsp;%15s&nbsp;&nbsp;&nbsp;&nbsp;%18s<br><br>" % (
            x['InstanceName'],
            x['PublicIpAddress'] if x['PublicIpAddress'] else '-',
            x['InnerIpAddress'] if x['InnerIpAddress'] else '-',
            x['groups'][0]['name'] if 'groups' in x and len(x['groups']) > 0 else '-')
    return HttpResponse(result.replace(" ", "&nbsp;"))


@login_required
def service_info(request):
    if request.method == "GET":
        kw = request.GET.get('kw', '')
        search_type = request.GET.get('search_type', '')
        return render(request, 'cmdb/cmdb.html', locals())

@login_required
def service_info_phone(request):
    if request.method == "GET":
        kw = request.GET.get('kw', '')
        search_type = request.GET.get('search_type', '')
        return render(request, 'cmdb/cmdb_phone.html', locals())

@login_required
def restart_service(request):
    task_id = request.POST.get('id')
    server_name = request.POST.get('server_name')
    commands_obj = ServerInfo.objects.filter(id=task_id)
    task_list = Runner.Task(name=server_name, module_name='shell', module_args='/root/test/didid.sh')
    runner = Runner(task_list=task_list, host_list=[commands_obj[0].InnerIpAddress])
    ret_info = runner.run()
    host_ip = []
    host_status = []
    host_msg = []
    host_name = [request.POST.get('host_name')]
    for i in ret_info[1].values():
        print('i#', i)
        for k, v in i.items():
            host_ip.append(k)
            host_status.append(v['status'])
            if host_status[0] == 'ok':
                host_msg = ['successful~']
            else:
                host_msg.append(v['result']['msg'])
    # return render(request, 'cmdb/cmdb_phone.html', locals())
    return JsonResponse({'status': host_status,'hostname': host_name, 'message': host_msg})

# 显示已删除的server信息
def show_del_server(request):
    if request.method == "GET":
        return render(request, 'cmdb/show_del_server_info.html', locals())

# 显示已删除的server信息
@page_handler
def del_list_page(request):
    kw2 = request.GET.get("kw2", "")
    area = request.GET.get("area", "")
    log.info('search by keyword: %s, area: %s' % (kw2, area))
    query = ServerInfo.objects.all().filter(enabled=1)
    if kw2:
        query = query.filter(Q(InstanceName__icontains=kw2) | Q(InnerIpAddress__icontains=kw2) |
                             Q(PublicIpAddress__icontains=kw2) | Q(Cpu__icontains=kw2) |
                             Q(Memory__icontains=kw2))
    return query


# 显示3天未更新的server信息
def show_update_info(request):
    if request.method == "GET":
        return render(request, 'cmdb/show_update_info.html', locals())

# 显示3天未更新的server信息
@page_handler
def update_status_page(request):
    kw3 = request.GET.get("kw3", "")
    area = request.GET.get("area", "")
    log.info('search by keyword: %s, area: %s' % (kw3, area))
    # 过滤出3天之前没更新的服务器
    query = ServerInfo.objects.all().filter(update_time__lte=datetime.datetime.utcnow() - datetime.timedelta(hours=64))
    if kw3:
        query = query.filter(Q(InstanceName__icontains=kw3) | Q(InnerIpAddress__icontains=kw3) |
                             Q(PublicIpAddress__icontains=kw3) | Q(Cpu__icontains=kw3) |
                             Q(Memory__icontains=kw3))
    return query


def update_info(request):
    """
    更新服务器信息
    :param request:
    :return:
    """
    if request.method == 'POST':
        srv = request.POST.getlist("id[]", [])
        print("srvvvvv", srv)
        update_server_info.delay(srv)   # celery异步任务开始，传参srv，srv形如[u'1972', u'1973', u'1974', u'2014', u'2015', u'1993', u'1764', u'1977', u'1983', u'2012']的一个列表
    return render(request, 'cmdb/cmdb.html', locals())


def do_operate(request):
    """
    do_operate：对数据库做操作，根据前端传过来的关键参数kws进行判断，进行删除或恢复操作
    :param request:
    :return:
    """
    srv = request.POST.getlist("id[]", [])
    kws = request.POST.get('kws')
    print("kws", kws)
    # console.log(image_id)
    log.info("start Remove server: " + str(srv))
    if not srv:
        log.error("Remove server not appoint!")
        return JsonResponse({'result': False, 'message': '请输入要删除的server ID'})
    try:
        if kws == 'remove':  # 删除
            srv_obj = ServerInfo.objects.filter(id__in=srv)
            for srv_id in srv_obj:
                srv_id.enabled = 1  # 状态值改为1，不可用
                srv_id.save()
                log.info('server delete Sucess！' + str(srv_id.InstanceName))
            return JsonResponse({'result': True, 'message': '删除成功'})
        elif kws == 'restore':  # 恢复
            srv_obj = ServerInfo.objects.filter(id__in=srv)
            for srv_id in srv_obj:
                srv_id.enabled = 0  # 状态值改为0，可用
                srv_id.save()
                log.info('server restore Sucess！' + str(srv_id.InstanceName))
            return JsonResponse({'result': True, 'message': '恢复成功'})
        elif kws == 'real_remove':  # 彻底删除
            srv_obj = ServerInfo.objects.filter(id__in=srv)
            for srv_id in srv_obj:
                srv_id.delete()
            return JsonResponse({'result': True, 'message': '彻底删除成功'})
        else:
            return JsonResponse({'result': False, 'message': '无关键字!'})

    except Exception as e:
        log.error("Server do_operate Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '删除失败：' + e.message})


def deeply_delete(request):
    """
    前端彻底删除按钮调用的函数
    :param request:
    :return:
    """
    srv= request.POST.getlist("id[]", [])
    try:
        for srv_id in srv:
            print("srv deep", srv_id)
            if not srv_id:
                log.error("Remove server not appoint!")
                return JsonResponse({'result': False, 'message': '请输入要彻底删除的server ID'})
            else:
                ServerInfo.objects.get(id=srv_id).delete()
                log.info("Server deeply_delete sucess!")
                return JsonResponse({'result': True, 'message': 'server 彻底删除成功。'})
    except Exception as e:
        log.error("Server deeply_delete Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '彻底删除失败：' + e.message})



def group_index(request):
    if request.method == 'GET':
        return render(request, 'cmdb/group.html', locals())

def eip_index(request):
    return render(request, 'cmdb/eip.html', locals())


def get_servers(request):
    sis = ServerInfo.objects.all()
    sis_data = [s.to_dict() for s in sis]
    return JsonResponse(sis_data)


@login_required
@page_handler
def group_page(request):
    sSearch = request.GET.get('sSearch', '')

    query = ServerGroup.objects.all()
    if sSearch:
        query = query.filter(Q(name__icontains=sSearch))
    return query


def add_group(request):
    if request.method == 'GET':
        server_infos = ServerInfo.objects.all()
        return render(request, 'cmdb/add_group.html', locals())
    else:
        name = request.POST.get("name", '')
        servers = request.POST.getlist("to", '')
        remark = request.POST.get("remark", '')
        if not name:
            pass
        server_list = ServerInfo.objects.filter(id__in=servers)
        sg = ServerGroup(name=name, remark=remark, count=len(servers), label=1)
        sg.save()
        sg.serverinfo_set.add(*server_list)

        return redirect(reverse('server:group'))


def update_group(request, gid):
    group = get_object_or_404(ServerGroup, pk=gid)
    if request.method == 'GET':
        if group.label == 1:
            server_infos = ServerInfo.objects.all()
            return render(request, 'cmdb/add_group.html', locals())
        else:
            return Http404()
    else:
        if not group.label == 1:
            raise Http404("Auto fetch group cannot modify!")
        name = request.POST.get("name", '')
        servers = request.POST.getlist("to", '')
        remark = request.POST.get("remark", '')
        if not name:
            pass
        server_list = ServerInfo.objects.filter(id__in=servers)
        group.name = name
        group.remark = remark
        group.count = len(servers)
        group.save()
        print(server_list)
        for old_server in group.serverinfo_set.all():
            if old_server not in server_list:
                group.serverinfo_set.remove(old_server)
        group.serverinfo_set.add(*server_list)

        return redirect(reverse('server:group'))


@login_required
def remove_group(request):
    group_id = request.POST.getlist("id[]", [])
    log.info("start Remove Server Group: " + str(group_id))
    if not group_id:
        log.error("Remove Group not appoint!")
        return JsonResponse({'result': False, 'message': '请输入要删除的Server ID'})

    try:
        group = ServerGroup.objects.filter(id__in=group_id)
        # for grp in group:
        #     grp.serverinfo_set = None
        group.delete()
        log.info('Group delete Sucess！' + str(group_id))
        return JsonResponse({'result': True, 'message': ''})
    except Exception as e:
        log.error("Group Remove Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '删除失败：' + e.message})


# 添加server按钮
def add_server(request):
    if request.method == "GET":
        server_form = AddServer()
        log.info('Into Add Server Page.')
        return render(request, 'cmdb/add_server.html', locals())
    else:
        log.info("start submit Add Server Data.")
        server_form = AddServer(request.POST)

        if server_form.is_valid():
            try:
                data = server_form.cleaned_data
                print("data server", data)
                srv = ServerInfo(
                    # InstanceName=data['name'],
                    InnerIpAddress=data['inner_ip'],
                    PublicIpAddress=data['outer_ip'],
                    server_location=data['area'],
                    RegionId=data['area'],
                    user=data['user'],
                    pwd=data['password'],
                    port=data['port'],
                    sn=data['sn'],
                    remark=data['remark']
                )
                if srv.insert(enc=True):
                    # 连接到主机，拷贝公钥
                    connect_server.delay(srv.id)

                    log.info("Insert Server data success!")
                    message = {'result': True, 'message': 'Server添加成功！', 'title': '添加Serve结果'}
                    return render(request, 'cmdb/add_server_result.html', locals())
                else:
                    log.error('Insert Server data  ERROR: ' + traceback.format_exc())
                    message = {'result': False, 'message': "Server添加失败，已存在相同的IP地址，请删除相同的IP地址后再次添加！！"}
                    return render(request, 'cmdb/add_server_result.html', locals())
            except Exception as e:
                log.error('Insert Server get the ERROR: ' + traceback.format_exc())
                message = {'result': False, 'message': '服务器发生异常：'+e.message + " 请稍候重试！"}
                return render(request, 'cmdb/add_server.html', locals())
        else:
            message = {'result': False, 'message': '表单验证失败！请检查您的填写。'}
            return render(request, 'cmdb/add_server.html', locals())


def check_ssh_copy(request):
    """
    添加server时候检测填写的ip地址等是否可ping通，如果不能ping通，则不让添加到数据库中去
    :param request:
    :return:
    """
    srv_inner_ip = request.POST.get('srv_inner_ip')
    srv_outer_ip = request.POST.get('srv_outer_ip')
    srv_user = request.POST.get('srv_user')
    srv_pwd = request.POST.get('srv_pwd')
    srv_port = request.POST.get('srv_port')
    connect_status = 0
    print("srv_inner_ip",srv_inner_ip)
    print("srv_outer_ip",srv_outer_ip)
    print("srv_user",srv_user)
    print("srv_pwd",srv_pwd)
    print("srv_port",srv_port)
    for ip_addr in [srv_inner_ip, srv_outer_ip]:
        if ip_addr:
            result = ssh_copy_id_passwd(ip_addr, srv_user, srv_pwd, srv_port)
            print("result", result)
            if result[0] == 0:
                print("连接成功")
                connect_status = 1
            else:
                print("连接失败")
                connect_status = 0
        if connect_status == 1:
            return JsonResponse({'result': True, 'message': '服务器连接成功！'})
        elif connect_status == 0:
            return JsonResponse({'result': False, 'message': '服务器连接失败！'})


def modify(request, srv_id):
    """
    modify Server by id 修改server按钮
    :param request:
    :param srv_id: server id
    :return:
    """
    try:
        if request.method == "GET":
            log.info('Into Update server page.')
            srvs = ServerInfo.objects.filter(id=srv_id)
            if srvs:
                srv = srvs[0]
                log.info("search success and prepage update Server: " + str(srv))
                return render(request, 'cmdb/add_server.html', locals())
            else:
                log.error("search Server <%s> error and turn to Add Server page." % srv_id)
                return render(request, 'cmdb/add_server.html', {"srv": None})
        else:
            server_form = AddServer(request.POST)

            if server_form.is_valid():
                data = server_form.cleaned_data
                srv = ServerInfo.objects.filter(id=srv_id)
                srv.update(
                    InstanceName=data['name'],
                    InnerIpAddress=data['inner_ip'],
                    PublicIpAddress=data['outer_ip'],
                    RegionId=data['area'],
                    user=data['user'],
                    pwd=des.encrypt(data['password']),
                    port=data['port'],
                    sn=data['sn'],
                    remark=data['remark']
                )
                # 更新数据字典，增加机房（如果不存在）
                DataOption(
                    category='area',
                    keyword=data['area']
                ).insert()
                message = {'result': True, 'message': 'Server修改成功！', 'title': '更新Serve结果'}
                return render(request, 'cmdb/add_server_result.html', locals())
            else:
                message = {'result': False, 'message': '表单验证失败！请检查您的填写。'}
                return render(request, 'cmdb/add_server.html', locals())
    except Exception as e:
        log.error("Modify  Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '更新失败：' + e.message})


@csrf_exempt
def add_server_api(request):
    """
    cmdb的api接口，用于服务器客户端初始化脚本调用，从而获取公钥内容以及创建server
    :param request: 接收url的get内容
    :return:
    """
    try:
        import os
        key_file = open(os.path.expandvars('$HOME')+"/.ssh/id_rsa.pub", 'r')  # os.path.expandvars('$HOME') ：获取当前用户家目录
        pubKeyContent = key_file.read()
        key_file.close()
        tmp_instanceid = "tmp-" + random_str()   # 生成临时instanceid，临时添加到数据库中，否则验证时候会报错

        server_api_form = AddServerApiForm(request.GET)  # 获取api url中get的内容
        if server_api_form.is_valid():
            data = server_api_form.cleaned_data
            inner_ip = data['innerIp']
            pub_ip = data['publicIp']
            srv_user = data['user']
            kw = data['kw']
            if not srv_user:
                srv_user = "root"
            srv_port = data['port']
            if not srv_port:
                srv_port = '8022'
            if kw.split("-")[1] == "ali":
                print("update ali server")
                get_ali_servers.delay()
                get_ali_disk_info.delay()
            elif kw.split("-")[1] == "ksy":
                print("update ksy server")
                get_ksyun.delay()
            elif kw == "xn-stand-server":
                srv = ServerInfo(
                    InnerIpAddress=inner_ip,
                    PublicIpAddress=pub_ip,
                    user=srv_user,
                    port=srv_port,
                    InstanceId=tmp_instanceid
                )
                if srv.insert(enc=True):  # 验证是否存在重复的IP地址,之后保存
                    res = {"result": True, "message": pubKeyContent}
                    return JsonResponse(res)
                else:  # 如果存在相同的IP地址则返回个错误信息
                    res = {"result": False, "message": "Has been the same IP, save failed!"}
                    return JsonResponse(res)
            else:
                print("update ksy and ali server")
                get_ali_servers()
                get_ali_disk_info()
                get_ksyun()
            res = {"result": True, "message": pubKeyContent}
            return JsonResponse(res)
        else:
            res = {"result": False, "message": "form is valid false!"}
            return JsonResponse(res)

    except Exception as e:
        traceback.print_exc()
        log.error(traceback.format_exc())
        res = {"result": False, "message": "key get error!" + e.message}
        return JsonResponse(res)


def tun_dest(server):
    region = server.RegionId
    if server.IpType == 'vpc':
        return 'tun3'
    elif region == 'cn-beijing':
        return 'tun0'
    elif region == 'cn-hangzhou':
        return 'tun1'
    elif region == 'cn-beijing-6':
        return 'tun2'
    elif region == 'cn-shanghai-2':
        return 'tun4'
    else:
        pass



def route_shell(request):
    servers = ServerInfo.objects\
        .filter(enabled=0, update_time__gt=datetime.datetime.utcnow() - datetime.timedelta(hours=64))\
        .filter(Q(RegionId='cn-beijing') | Q(RegionId='cn-beijing-6') | Q(RegionId='cn-hangzhou'))
    shell = ['#!/bin/bash']
    for server in servers:
        if server.InnerIpAddress:
            shell.append("ip route add %s dev %s" % (server.InnerIpAddress, tun_dest(server)))
    return HttpResponse('\n'.join(shell))
