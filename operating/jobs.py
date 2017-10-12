#!/usr/bin/python
# coding:utf-8
import traceback
import os
from service.logic import run_task
import json
import datetime
from server.models import Server
from operating.logic import Tasks, run_multi_tasks
from operating.models import FileTransfer, TaskRecord, RunScript, Job
from celery.task import task
from tempfile import NamedTemporaryFile
from common.util.ansible_api import Runner
from cmdb.models import ServerInfo
from common.util.ansible_api import ResultsCollector


@task
def run_job(job_id='', account='', run_type=0):
    """
    运行作业多个任务
    :param job_id: 作业ID
    :param account: 执行人
    :param run_type: 执行类型（默认为0 网页执行）。（1 crontab执行）
    :return:
    """
    job = Job.objects.get(id=job_id)
    tasks = job.task_id.split(',')
    job.current_task = tasks[0]
    job.status = 0
    job.save()

    start_time = datetime.datetime.utcnow()
    task_list = []
    try:
        for task in tasks:
            # job.current_task = task
            # job.save()
            print("task", task)
            print("--------------------------------------------")
            task_rs_obj = RunScript.objects.filter(id=task)  # 执行结果为一个列表
            task_ft_obj = FileTransfer.objects.filter(id=task) # 执行结果为一个列表
            # 如果是执行脚本
            if task_rs_obj:  # 如果列表不为空，则为执行脚本的任务
                task_list.append(gen_runscript_task(task))
            # 如果是分发文件
            if task_ft_obj:  # 如果列表不为空，则为分发文件的任务
                _tmp_task = gen_filetransfer_task(task)
                if isinstance(_tmp_task, list):
                    task_list.extend(_tmp_task)
                else:
                    task_list.append(_tmp_task)
        inv = [si.ansible_host for si in ServerInfo.objects.filter(id__in=job.server.split(','))]
        runner = Runner(task_list=task_list, host_list=inv)
        code, res = runner.run(callback=FileTransferResultsCollector(jobid=job_id))
        end_time = datetime.datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        TaskRecord(account=account,
                   task_id=str(job.id),
                   start_time=start_time,
                   end_time=end_time,
                   total_time=total_time,
                   run_type=run_type,
                   task_type='job'
                   ).save()
        job.current_task = ''
        job.status = 1
        job.save()
    except Exception as e:
        traceback.print_exc()


class FileTransferResultsCollector(ResultsCollector):
    """
    Job执行批量作业所使用的回调, 目的是记录每个文件分发任务的子任务的关联, 合并结果
    """

    def __init__(self, jobid, *args, **kwargs):
        super(FileTransferResultsCollector, self).__init__(*args, **kwargs)
        self.jobid = jobid
        self.job = Job.objects.safe_get(id=jobid)
        self.task_map = {}
        self.sep = ' -> '

    def v2_runner_on_ok(self, result, *args, **kwargs):
        ip = result._host.get_name()
        task_name = result._task.name

        if task_name.find(self.sep) > 0:
            parent_name, sub_name = task_name.split(self.sep)
            self.result.setdefault(parent_name, {})
            self.result[parent_name].setdefault(ip, {})
            self.result[parent_name][ip][sub_name] = {'status': 'ok', 'result': result._result}

        else:
            self.result.setdefault(task_name, {})
            self.result[task_name].setdefault(ip, {})
            self.result[task_name][ip] = {'status': 'ok', 'result': result._result}

    def v2_runner_on_failed(self, result, *args, **kwargs):
        ip = result._host.get_name()
        task_name = result._task.name

        if task_name.find(self.sep) > 0:
            parent_name, sub_name = task_name.split(self.sep)
            self.result.setdefault(parent_name, {})
            self.result[parent_name].setdefault(ip, {})
            self.result[parent_name][ip][sub_name] = {'status': 'failed', 'result': result._result}

        else:
            self.result.setdefault(task_name, {})
            self.result[task_name].setdefault(ip, {})
            self.result[task_name][ip] = {'status': 'failed', 'result': result._result}

    def v2_runner_on_unreachable(self, result):
        ip = result._host.get_name()
        task_name = result._task.name

        if task_name.find(self.sep) > 0:
            parent_name, sub_name = task_name.split(self.sep)
            self.result.setdefault(parent_name, {})
            self.result[parent_name].setdefault(ip, {})
            self.result[parent_name][ip][sub_name] = {'status': 'unreachable', 'result': result._result}
        else:
            self.result.setdefault(task_name, {})
            self.result[task_name].setdefault(ip, {})
            self.result[task_name][ip] = {'status': 'unreachable', 'result': result._result}

    def v2_playbook_on_task_complete(self):
        # 每次执行完一个任务(所有的主机)回调该方法
        _task = RunScript.objects.safe_get(id__in=self.job.task_id.split(','), name=self.current_task.name)
        if _task:
            start_time = datetime.datetime.utcnow()
            end_time = datetime.datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()
            tr = TaskRecord(account='fengxu',
                            task_id=str(_task.id),
                            start_time=start_time,
                            run_type=0,
                            task_type='job_bash',
                            total_time=total_time
                            )
            tr.save()
            print('*****', self.result[self.current_task.name])
            _result, flag = run_results(self.result[self.current_task.name])
            tr.result = json.dumps(_result)
            tr.save()

            rs = RunScript.objects.get(id=_task.id.get_hex())
            rs.status = 1 if flag else 2
            rs.save()
        else:
            if self.current_task.name.find(self.sep) > 0:
                task_name, sub_name = self.current_task.name.split(self.sep)
                _task = FileTransfer.objects.safe_get(id__in=self.job.task_id.split(','), name=task_name)
                if not _task:
                    return

                start_time = datetime.datetime.utcnow()
                end_time = datetime.datetime.utcnow()
                total_time = (end_time - start_time).total_seconds()
                tr = TaskRecord.objects.safe_get(task_id=str(_task.id))
                if not tr:
                    tr = TaskRecord(account='fengxu', run_type=0, task_id=_task.id.get_hex(), start_time=start_time,
                                    end_time=end_time, total_time=total_time, task_type='job_filetransfer')
                    tr.save()
                    old_result = None
                else:
                    old_result = json.loads(tr.result) if tr.result else None

                new_result, flag = analyze_job_filetransfer_result(self.result[task_name], old_result)
                tr.result = json.dumps(new_result)
                tr.save()
                ft = FileTransfer.objects.get(id=str(_task.id))
                ft.status = 1 if flag else 2
                ft.save()

            else:
                _tasks = FileTransfer.objects.filter(id__in=self.job.task_id.split(','), name=self.current_task.name)
                task_name = self.current_task.name
                pass


# 运行脚本任务
def runscript_task(task, li_rs_srv, account, run_type):
    li_rem_host = [srv.ansible_host for srv in Server.objects.filter(id__in=li_rs_srv) if srv.ansible_host]  # 注意这里id__in=后面要跟一个列表
    commands_obj = RunScript.objects.filter(id=task)
    commands_from_mysql = commands_obj[0].script_content
    file_path = save_tmp_script(commands_from_mysql)
    start_time = datetime.datetime.utcnow()
    r_result = run_task(li_rem_host, module_name='script', module_args=file_path)  # 运行脚本
    end_time = datetime.datetime.utcnow()
    total_time = (end_time - start_time).total_seconds()
    # 把run_task的执行返回结果，转化为列表，为后面传参做准备
    li_r_result = []
    li_r_result.append(r_result)
    # print "li_r_result", li_r_result
    try:
        tr = TaskRecord(account=account,
                        task_id=task,
                        start_time=start_time,
                        end_time=end_time,
                        total_time=total_time,
                        run_type=run_type,
                        task_type='job_bash'
                        )
        tr.save()
        tr.result, flag = run_results(li_r_result)
        tr.result = json.dumps(tr.result)
        tr.save()
        rs = RunScript.objects.get(id=task)
        rs.status = 1 if flag else 2
        rs.save()
    except Exception as e3:
        traceback.print_exc()


def gen_runscript_task(task_id):
    """
    生成执行脚本的Task任务
    :param task_id: 任务ID
    :param server_list: 服务器列表
    :return: Runner.Task对象
    """
    commands_obj = RunScript.objects.filter(id=task_id)
    commands_from_mysql = commands_obj[0].script_content
    file_path = save_tmp_script(commands_from_mysql)

    return Runner.Task(name=commands_obj[0].name, module_name='script', module_args=file_path)



def gen_filetransfer_task(task_id):
    """
    生成分发文件的Task列表
    :param task_id: 任务ID
    :return: Runner.Task对象的列表
    """
    ft_obj = FileTransfer.objects.filter(id=task_id)
    f_path = ft_obj[0].files_path
    dest = ft_obj[0].dest_path
    li_f_path = f_path.split('||')
    task_list = []
    for file_path in li_f_path:
        sub_task_name = ft_obj[0].name + ' -> ' + (file_path[file_path.rfind('/') + 1:] if file_path.rfind('/') >= 0 else file_path)
        task_list.append(Runner.Task(name=sub_task_name,
                         module_name='copy', module_args={"src": file_path, "dest": dest},
                         _id=task_id, super_task_name=ft_obj[0].name))
    return task_list


def filetransfer_task(task, li_fp_srv, account, run_type):
    li_rem_host = [srv.ansible_host for srv in Server.objects.filter(id__in=li_fp_srv)]
    print("li_rem_host22222222", li_rem_host)
    ft_obj = FileTransfer.objects.filter(id=task)
    f_path = ft_obj[0].files_path
    dest = ft_obj[0].dest_path
    li_f_path = f_path.split('||')
    tsk = [Tasks(li_rem_host, module_name='copy', module_args='src=%s' % fp + ' dest=%s' % dest) for fp in li_f_path]
    # for fp in li_f_path:
    #     tsk.append(Tasks(li_rem_host, module_name='copy', module_args='src=%s' % fp + ' dest=%s' % dest))
    start_time = datetime.datetime.utcnow()
    result = run_multi_tasks(tsk)  # 开始传输文件
    end_time = datetime.datetime.utcnow()
    total_time = (end_time - start_time).total_seconds()
    tr = TaskRecord(account=account, run_type=run_type, task_id=task, start_time=start_time, end_time=end_time, total_time=total_time, task_type='job_filetransfer')
    tr.save()
    tr.result, flag = analyze_filetransfer_result(result)
    tr.result = json.dumps(tr.result)
    tr.save()
    ft = FileTransfer.objects.get(id=task)
    ft.status = 1 if flag else 2
    ft.save()


def analyze_filetransfer_result(result):
    """
    解析分发文件多任务的返回值，使结果以IP地址为key，文件名为二级key，值为result和message的字典
    :param result:
    :return:
    """
    data = {}
    flag = True
    for _task_name, line in list(result.items()):
        for ip, rs in list(line.items()):
            data.setdefault(ip, {})
            if rs['status'] == 'unreachable':
                data[ip]['dark'] = {'result': False, 'message': rs['result']['msg']}
                flag = False
            else:
                file_name = _task_name[_task_name.rfind('/') + 1:]
                if _task_name.find('libselinux-python') > 0:
                    if rs['status'] == 'failed':
                        file_name = '分发预环境 libselinux-python'
                    elif rs['status'] == 'ok':
                        continue
                if rs['status'] == 'failed':
                    data[ip]["File " + file_name] = {'result': False, 'message': rs['result']['msg']}
                else:
                    data[ip]["File " + file_name] = {'result': True, 'message': ''}

    print("data1", data)
    return data, flag


def analyze_job_filetransfer_result(result, pristine=None):
    """
    解析job多个作业的返回值，使结果以IP地址为key，文件名为二级key，值为result和message的字典
    :param result: 本次任务生成的结果
    :param pristine: 原来的字典数据, 用于合并多个任务的结果
    :return:
    """
    data = pristine if pristine else {}
    flag = True

    for ip, line in list(result.items()):
        data.setdefault(ip, {})
        for filename, results in list(line.items()):
            data[ip].setdefault(filename, {})
            if results['status'] == 'ok':
                data[ip][filename] = {'result': True, 'message': ''}
            else:
                flag = False
                data[ip][filename] = {'result': False, 'message': results['result']['msg']}
    return data, flag


def save_tmp_script(content, new_name=''):
    """
    缓存文件夹生成可执行脚本。
    :param content: 脚本内容
    :param new_name: 可指定该值修改脚本名称
    :return: 返回脚本文件的全路径
    """
    if not content:
        return None
    # 去掉\r回车符
    content = content.replace('\r', '')
    # 生成缓存文件
    hosts = NamedTemporaryFile('w', delete=False, encoding='utf-8')
    hosts.write(content)
    hosts.close()
    file_dir, file_name = os.path.split(hosts.name)
    os.chdir(file_dir)
    if new_name:
        # 修改为指定名称
        os.rename(file_name, new_name)
        file_name = new_name
    file_path = os.path.join(file_dir, file_name)
    # 赋予可读可执行权限
    os.chmod(file_path, 0o555)
    return file_path


# 构造脚本执行后，返回结果的函数，用于存入数据库之用
def run_results(result):
    data = {}
    flag = True
    for ip, rs in list(result.items()):
        data.setdefault(ip, {})
        if rs['status'] == 'unreachable':
            data[ip]['dark'] = {'result': False, 'message': rs['result']['msg']}
            flag = False
        elif rs['status'] == 'failed':
            err_msg = ''
            if 'msg' in rs['result']:
                err_msg += rs['result']['msg']
            if 'stdout' in rs['result'] and rs['result']['stdout']:
                err_msg += "\nstdout: " + rs['result']['stdout']
            if 'stderr' in rs['result'] and rs['result']['stdout']:
                err_msg += '\nstderr: ' + rs['result']['stderr']
            data[ip] = {'result': False, 'message': err_msg}
        else:
            data[ip] = {'result': True, 'message': rs['result']['stdout']}

    return data, flag


