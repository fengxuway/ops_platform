#!/usr/bin/python
# coding:utf-8
from django.http import JsonResponse
from django.shortcuts import render, redirect
from common.forms import PageData
import logging
import traceback
import os, subprocess
import re
from operating.forms import RunScriptForm
from service.logic import run_task
import json
import datetime
from django.conf import settings
from server.models import Server
from common.views import handle_uploaded_file
from django import forms
from operating.logic import Tasks, run_multi_tasks
from operating.models import FileTransfer, TaskRecord, RunScript, Job, CronJob
from operating.forms import FileTransferForm, CronjobForm
from django.contrib.auth.decorators import login_required
from django.db.models import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from service.logic import ansible_ip
from common.util.id_creater import random_str
from operating.jobs import run_job
from operating.jobs import run_results
from operating.jobs import analyze_filetransfer_result
from operating.jobs import save_tmp_script
from common.views import page_handler
from django.db.models import Q
from common.util.ansible_api import Runner
from cmdb.models import ServerInfo


log = logging.getLogger('django')


def create_name(word):
    """
    生成名字
    :param word: 用于生成名字，是生成名字的前缀
    :return:
    """
    words = word + '-' + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return words


def index(request):
    """
    快速脚本执行
    :param request:
    :return:
    """
    name = create_name('执行脚本')
    if request.method == 'GET':
        srv_param = request.GET.get("server", None)
        print(request.GET)
        if srv_param:
            server_ids = srv_param.split(',')
            srvs = ServerInfo.objects.filter(id__in=server_ids)
            servers = [srv.to_dict() for srv in srvs]
        return render(request, 'operating/index.html', locals())
    if request.method == "POST":
        user = request.POST.get('user')
        runscript_form = RunScriptForm(request.POST)
        try:
            if runscript_form.is_valid():
                data = runscript_form.cleaned_data
                print("data", data)
                script_data = RunScript(
                    name=name,
                    user=data['user'],
                    script_content=data['script_content'],
                    server=data['server'],
                    script_args=data['script_args'],
                    )
                script_data.save()

                tsk_id = str(script_data.id)
                li_srv = data['server'].split(",")
                li = [srv.ansible_host for srv in ServerInfo.objects.filter(id__in=li_srv)]  # 构造ansible_host列表
                if not li:
                    raise Exception("No Server Selected!")
                file_path = save_tmp_script(script_data.script_content)
                start_time = datetime.datetime.utcnow()
                r_result = run_task(li, module_name='script', module_args=file_path + " " + script_data.script_args)  # 运行脚本
                end_time = datetime.datetime.utcnow()
                total_time = (end_time - start_time).total_seconds()

                tr = TaskRecord(account=request.user.username,
                                start_time=start_time,
                                task_id=tsk_id,
                                end_time=end_time,
                                total_time=total_time,
                                run_type=0,
                                task_type='bash'
                                )
                tr.result, flag = run_results(r_result)
                tr.result = json.dumps(tr.result)
                tr.save()
                script_data.status = 1 if flag else 2
                script_data.save()
                return JsonResponse({'result': True, 'message': str(tr.result)})
            else:
                log.error("Form data ERROR: " + str(runscript_form.errors))
                message = '表单验证失败！请检查您的填写内容。'+ str(runscript_form.errors)
                return JsonResponse({'result': False, 'message': message})
        except Exception as e:
            log.error(traceback.format_exc())
            message = e.message
            return JsonResponse({'result': False, 'message': message})


@page_handler
def page(request):
    query = CronJob.objects.all()
    return query


@login_required
def cronjobs(request):
    return render(request, 'operating/cronjob.html', locals())


def add_cronjobs(request):
    """
    添加计划任务
    :param request:
    :return:
    """
    cron_name = create_name('cron')
    if request.method == 'GET':
        return render(request, 'operating/add_cronjob.html', locals())

    if request.method == "POST":
        servers = request.POST.getlist('server')
        cronjobform = CronjobForm(request.POST)
        if cronjobform.is_valid():
            try:
                data = cronjobform.cleaned_data
                # 校验crontab表达式是否正确
                li_contents = data['cron_content'].split(' ')
                if len(li_contents) != 5:
                    msg = "对不起，表单验证失败，CRON表达式错误！"
                    return render(request, 'operating/add_cronjob_result.html', locals())
                str_server = ','.join(servers)
                # 保存到数据库
                cronjob_data = CronJob(
                    name=data['name'],
                    cron_creater=request.user.username,
                    script_content=data['script_content'],
                    cron_content=data['cron_content'],
                    server=str_server,
                    cron_modified=request.user.username,
                    )
                cronjob_data.save()  # 定时作业信息存数据库

                # 推送脚本到目标主机
                ## 获取server的ansible列表
                li_rem_host = [srv.ansible_host for srv in ServerInfo.objects.filter(id__in=servers)]
                ## 生成shell脚本
                src = save_tmp_script(cronjob_data.script_content, new_name=data['name']+'.sh')
                dest = settings.CRON_SHELL_PATH
                ## 执行ansible任务
                run_task(li_rem_host, module_name='copy', module_args='src=%s dest=%s mode=0755' % (src, dest))

                msg = "定时任务作业保存成功！"
                return render(request, 'operating/add_cronjob_result.html', locals())
            except Exception as e3:
                log.error(traceback.format_exc())
                msg = "定时任务作业保存失败！"
                return render(request, 'operating/add_cronjob_result.html', locals())
        else:
            msg = "对不起，表单验证失败，请重新输入！"
            return render(request, 'operating/add_cronjob_result.html', locals())


@login_required
def fileupload(request):
    """
    文件上传到缓存目录，并返回上传的绝对路径
    :param request:
    :return:
    """
    class UploadForm(forms.Form):
        uploadFile = forms.FileField(required=True)
    form = UploadForm(request.POST, request.FILES)

    log.info('sucess upload!')
    try:
        if form.is_valid():  # 验证表单提交是否正确
            data = form.cleaned_data
            log.info(data)
            # 缓存上传路径
            path = os.path.join(settings.TMP_DIR, 'upload')
            file_path = handle_uploaded_file(path, data['uploadFile'])

            return JsonResponse({'result': True, 'path': file_path, 'file_name': data['uploadFile'].name})
        return JsonResponse({'result': False, 'message': '表单验证失败！'})
    except Exception as e:
        log.error(traceback.format_exc())
        return JsonResponse({'result': False, 'message': '发生异常：' + e.__class__.__name__})


@login_required
def add_job(request):
    if request.method == "GET":
        srv_param = request.GET.get("server", None)
        print(request.GET)
        if srv_param:
            server_ids = srv_param.split(',')
            srvs = ServerInfo.objects.filter(id__in=server_ids)
            servers = [srv.to_dict() for srv in srvs]
        return render(request, 'operating/add_job.html', locals())
    else:
        post = request.POST
        id_order = post.getlist("id_order", [])
        task_ids = []
        _name = post.get('name', '')
        is_total_server_str = post.get('is_total_server', '')
        is_total_server = False
        total_server_ids = []
        if is_total_server_str and is_total_server_str == 'true':
            is_total_server = True
            total_server_ids = post.getlist("server_ids_all", [])
            if not total_server_ids:
                return JsonResponse({'result': False, 'message': '您尚未选择目标服务器'})
        for _id in id_order:
            prefix = '_' + _id

            _type = post.get('type' + prefix, '')  # file or script
            _title = post.get('title' + prefix, '')
            _user = post.get('user' + prefix, '')  # root or other
            _server_ids = total_server_ids if is_total_server else post.getlist('server_ids' + prefix, []) # 服务器ID列表
            if _type == 'file':
                _path = post.get('path' + prefix, '')
                _file_path = post.getlist('file_path' + prefix, [])
                ft = FileTransfer(name=_title, user=_user, files_path='||'.join(_file_path), dest_path=_path, server=','.join(_server_ids))
                ft.save()
                task_ids.append(str(ft.id))
            elif _type == 'script':
                _script_content = post.get('script_content' + prefix, '')
                if _script_content:
                    _script_content = _script_content.replace('\r', '')
                _args = post.get('args' + prefix, '')
                rs = RunScript(name=_title, user=_user, server=','.join(_server_ids), script_content=_script_content, script_args=_args)
                rs.save()
                task_ids.append(str(rs.id))

        print(task_ids)
        try:
            job = Job(name=_name, task_id=','.join(task_ids), current_task=task_ids[0], server=','.join(total_server_ids))
            job.save()
            run_job.delay(job_id=str(job.id), account=request.user.username)

            return redirect(reverse('operating:job_result', kwargs={'job_id': str(job.id)}))
        except Exception:
            log.error(traceback.format_exc())
            return JsonResponse({'result': False, 'message': '发生异常：' + traceback.format_exc()})


@login_required
def job_result(request, job_id):
    # job_id = request.GET.get("id")
    job = get_object_or_404(Job, pk=job_id)
    task_ids = job.task_id.split(',')
    tasks = []
    for task_id in task_ids:
        _rs = RunScript.objects.filter(id=task_id)
        if _rs:
            tasks.append(_rs[0])
        else:
            _ft = FileTransfer.objects.filter(id=task_id)
            if _ft:
                tasks.append(_ft[0])
    return render(request, 'operating/job_result.html', locals())


@login_required
def job_process(request, job_id):
    """
    查看作业运行进度
    :param request:
    :param job_id:
    :return:
    {

        current_task: 'KDLSNMSDFKKS',
        data:{
            'task_id_1': '{"result"......,
            'task_id_2': '{"result"......,

        }
    }

    {result: True or Flse, message:'****'}

    """
    job = get_object_or_404(Job, pk=job_id)
    try:
        current_task_id = request.POST.get('current_task', '')

        task_ids = job.task_id.split(',')
        result = dict()
        result['current_task'] = job.current_task
        result['data'] = {}
        start = task_ids.index(current_task_id) if current_task_id in task_ids else 0
        end = task_ids.index(job.current_task) if job.current_task in task_ids else len(task_ids)
        for i in range(start, end):
            _task_id = task_ids[i]
            tasks = TaskRecord.objects.filter(task_id=_task_id).order_by('-create_time')
            if tasks:
                task = tasks[0]
                result['data'][_task_id] = task.to_dict()
        print(result)
        return JsonResponse(result)
    except Exception as e:
        log.info(traceback.format_exc())
        return JsonResponse({'result': False, 'message': '发生异常：' + e.__class__.__name__})


@login_required
def job_list(request):
    if request.method == 'GET':
        return render(request, 'operating/list.html', locals())


@login_required
@page_handler
def job_list_page(request):
    kw = request.GET.get("kw", "")
    area = request.GET.get("area", "")
    log.info('search by keyword: %s, area: %s' % (kw, area))
    query = TaskRecord.objects.filter(Q(task_type='job') | Q(task_type='filetransfer') | Q(task_type='bash'))
    if kw:
        pass
    return query


@login_required
def filetransfer(request):
    if request.method == "GET":
        ft_name = create_name('分发文件')
        srv_param = request.GET.get("server", None)
        if srv_param:
            server_ids = srv_param.split(',')
            srvs = ServerInfo.objects.filter(id__in=server_ids)
            servers = [srv.to_dict() for srv in srvs]
        return render(request, 'operating/filetransfer.html', locals())

    tasks = []
    form = FileTransferForm(request.POST)
    if form.is_valid():
        try:
            ft_name = create_name('分发文件')
            data = form.cleaned_data
            print(data)
            srvs = [ServerInfo.objects.get(id=i).ansible_host for i in data['server_ids']]
            print(srvs)
            ft = FileTransfer(name=ft_name, user=data['user'], files_path='||'.join(data['file_path']), dest_path=data['dest'],
                              server=','.join(data['server_ids']))
            ft.save()
            start_time = datetime.datetime.utcnow()
            tr = TaskRecord(account=request.user.username,
                            start_time=start_time,
                            task_id=ft.id,
                            task_type='filetransfer')
            tr.save()

            task_list = [Runner.Task(name='be sure libselinux-python are installed', module_name='yum',
                        module_args={'name': 'libselinux-python', 'state': 'present'})]
            for fp in data['file_path']:
                task_list.append(Runner.Task(name='copy file ' + fp, module_name='copy', module_args={'src': fp, 'dest': data['dest']}))
            # pb = Runner.Playbook(task_list=task_list)
            rc, result = Runner(host_list=srvs, task_list=task_list).run()
            tr.result, flag = analyze_filetransfer_result(result)
            tr.result = json.dumps(tr.result)
            ft.status = 1 if flag else 2
            ft.save()
            tr.end_time = datetime.datetime.utcnow()
            tr.total_time = (tr.end_time - start_time).total_seconds()
            tr.save()
            return JsonResponse({'result': True, 'message': '执行完毕', 'data': tr.to_dict()})
        except Exception as e:
            traceback.print_exc()
            log.error(traceback.format_exc())
    else:
        print("验证失败")
        print(form.errors)


def cron_update(request, crn_id):
    """
    更新计划任务
    :param request:
    :param crn_id: 计划任务id
    :return:
    """
    if request.method == "GET":
        crn_ids = CronJob.objects.filter(id=crn_id)
        if crn_ids:
            crn_obj = crn_ids[0]
            return render(request, 'operating/add_cronjob.html', locals())
    else:
        crn_ids = CronJob.objects.filter(id=crn_id)
        server_items = ServerInfo.objects.all()
        cron_form = CronjobForm(request.POST)

        if cron_form.is_valid():
            print("cron_form", cron_form)
            servers = request.POST.getlist('server')
            str_srv = ""
            str_server = ','.join(servers)
            print("str_server2222", str_server)
            data = cron_form.cleaned_data
            print("data", data)
            crn = CronJob.objects.filter(id=crn_id)
            crn.update(
                name=data['name'],
                cron_creater=request.user.username,
                script_content=data['script_content'],
                cron_content=data['cron_content'],
                server=str_server,
                cron_modified=request.user.username,
            )
            # 更新脚本内容
            servs_obj = CronJob.objects.get(id=crn_id)
            print("servs_obj", servs_obj.server)
            servs = servs_obj.server
            cron_name = servs_obj.name
            li_servs = servs.split(',')
            li_rem_host = [srv.ansible_host for srv in ServerInfo.objects.filter(id__in=li_servs)]
            commands_from_mysql = servs_obj.script_content
            new_path = save_tmp_script(commands_from_mysql, cron_name+'.sh')
            # 传输本地保存的cron文件到远程主机
            src = new_path
            dest = '/data/upload/crontab/'
            tsk = [Tasks(li_rem_host, module_name='copy', module_args='src=%s' % src + ' dest=%s' % dest)]
            result = run_multi_tasks(tsk)  # 开始传输文件
            # 授权文件具备执行权限
            cmds = 'chmod +x ' + dest+cron_name+'.sh'
            log.info('Beginning update cron !')
            run_task(li_rem_host, module_name='command', module_args=cmds)
            log.info('Update cron completed !')
            msg = "计划任务更新成功!"
            return render(request, 'operating/add_cronjob_result.html', locals())
        else:
            msg = "对不起，表单验证失败，请确认填写信息！"
            return render(request, 'operating/add_cronjob_result.html', locals())


def remove_cron_line(request):
    """
    删除计划任务
    :param request:
    :return:
    """
    cron_id = request.POST.getlist("id[]", [])
    print("cron_id_del_test", cron_id)
    log.info("start Remove cron: " + str(id))
    if not cron_id:
        log.error("Remove cron not appoint!")
        return JsonResponse({'result': False, 'message': '请输入要删除的Cron ID'})
    try:
        # 停止计划任务
        re_cron_id = cron_id[0].replace('-', '')  # 去掉‘-’
        cron_obj = CronJob.objects.filter(id=re_cron_id)
        cron_name = cron_obj[0].name
        servers = cron_obj[0].server
        li_srv = servers.split(',')
        li_rem_host = [srv.ansible_host for srv in ServerInfo.objects.filter(id__in=li_srv)]
        cron_cmd = 'name="'+cron_name+'"'+' '+'state=absent'
        log.info('Set disable cron!')
        run_task(li_rem_host, module_name='cron', module_args=cron_cmd)
        log.info('Set disable cron completed!')
        # 删除计划任务
        cron = CronJob.objects.filter(id__in=cron_id)
        cron.delete()
        log.info('Cron delete Sucess！' + str(id))
        return JsonResponse({'result': True, 'message': '删除计划任务成功！'})
    except Exception as e:
        log.error("Cron Remove Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '删除失败：' + e.message})


def start_cron(request):
    """
    启用计划任务
    :param request:
    :return:
    """
    try:
        cron_id = request.POST.get('id')  # 从前端点击停止/启动按钮时，获取id值
        re_cron_id = cron_id.replace('-', '')  # 去掉‘-’
        cron_obj = CronJob.objects.filter(id=re_cron_id)
        cron_name = cron_obj[0].name
        servers = cron_obj[0].server
        li_srv = servers.split(',')
        li_rem_host = [srv.ansible_host for srv in ServerInfo.objects.filter(id__in=li_srv)]
        dest_cron_name = '/data/upload/crontab/'+cron_name+'.sh'
        print("dest_cron_name", dest_cron_name)
        cron_contents = cron_obj[0].cron_content  # 从前端取出计划任务内容
        contents = cron_contents.split(' ')  # 将取出的计划任务内容转化为列表
        cron_cmd = 'minute='+contents[0]+' '+'hour='+contents[1]+' '+'day='+contents[2]+' '+'month='+contents[3]+' '+'weekday='+contents[4]+' '+'job="'+'/bin/sh '+dest_cron_name+'"'+' '+'name="'+cron_name+'"'+' '+'state=present'
        log.info('Set enable cron!')
        log.info("CRON shell: " + cron_cmd)
        run_task(li_rem_host, module_name='cron', module_args=cron_cmd) # 执行
        log.info('Set enable cron completed!')
        cron_line = CronJob.objects.get(id=re_cron_id)
        cron_line.status = 1
        cron_line.save()
        return JsonResponse({'result': True, 'message': '计划任务启动成功'})
    except Exception as e:
        log.error("Cron start Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '计划任务启动失败：' + e.message})


def stop_cron(request):
    """
    停用计划任务
    :param request:
    :return:
    """
    try:
        cron_id = request.POST.get('id')  # 从前端点击停止/启动按钮时，获取id值
        re_cron_id = cron_id.replace('-', '')  # 去掉‘-’
        cron_obj = CronJob.objects.filter(id=re_cron_id)
        cron_name = cron_obj[0].name
        servers = cron_obj[0].server
        li_srv = servers.split(',')
        li_rem_host = [srv.ansible_host for srv in ServerInfo.objects.filter(id__in=li_srv)]
        cron_cmd = 'name="'+cron_name+'"'+' '+'state=absent'
        log.info('Set disable cron!')
        run_task(li_rem_host, module_name='cron', module_args=cron_cmd)  # 停用计划任务
        log.info('Set disable cron completed!')
        cron_line = CronJob.objects.get(id=re_cron_id)
        cron_line.status = 0
        cron_line.save()
        return JsonResponse({'result': True, 'message': '计划任务停止成功'})
    except Exception as e:
        log.error("Cron stop Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '计划任务停用失败：' + e.message})