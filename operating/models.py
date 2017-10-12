# coding:utf-8

from common.models import BaseModel
from django.db import models
import uuid
from django.utils import timezone


class RunScript(BaseModel):
    id = models.UUIDField('uuid', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('脚本名称', max_length=200, blank=True, null=True)
    user = models.CharField('执行账户', max_length=100, default='root', null=True)
    server = models.CharField('目标机器', max_length=10000, blank=True, null=True)
    script_content = models.TextField('脚本内容', blank=True, null=True)
    script_args = models.CharField('脚本参数', max_length=100, null=True, blank=True)
    # timeout = models.IntegerField(u'超时时间', null=True, blank=True)
    # run_path = models.CharField(u'运行目录', max_length=200, blank=True, null=True)

    status = models.IntegerField('任务状态', default=-1)
    '''
    -1: 未执行
    0：正在执行
    1：执行成功
    2：执行失败
    '''

    def __unicode__(self):
        return "RunScript<%s>" % self.name

    class Meta:
        verbose_name = '脚本执行'
        permissions = (('view_runscript', '访问' + verbose_name),)


class FileTransfer(BaseModel):
    id = models.UUIDField('uuid', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('任务名', max_length=200, blank=True, null=True)
    user = models.CharField('执行账户', max_length=100, default='root', null=True)
    files_path = models.CharField('文件存储路径', max_length=200, blank=True, null=True)
    dest_path = models.CharField('目标存储路径', max_length=200, blank=True, null=True)
    server = models.CharField('目标主机', max_length=200, blank=True, null=True)

    status = models.IntegerField('任务状态', default=-1)
    '''
    status：
    -1: 未执行
    0：正在执行
    1：执行成功
    2：执行失败
    '''

    def split_server(self):
        return self.server.split(',')

    def split_files_path(self):
        return self.files_path.split('||')

    def __unicode__(self):
        return "FileTransfer<%s>" % self.name

    class Meta:
        verbose_name = '文件分发'
        permissions = (('view_filetransfer', '访问' + verbose_name),)


class Job(BaseModel):
    id = models.UUIDField('uuid', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('任务名', max_length=200, blank=True, null=True)
    task_id = models.CharField('任务ID列表 逗号分割', max_length=1000, blank=True, null=True)
    status = models.IntegerField('任务状态', default=-1)
    current_task = models.CharField('当前执行到的任务', max_length=40, blank=True, null=True)
    server = models.CharField('目标主机', max_length=10000, blank=True, null=True)

    class Meta:
        verbose_name = '作业管理'
        permissions = (('view_job', '访问' + verbose_name),)


class TaskRecord(BaseModel):
    result = models.TextField('执行结果', null=True, blank=True)
    account = models.CharField('CMS登陆用户', max_length=100, null=True)
    start_time = models.DateTimeField('执行脚本时间', blank=True, null=True)
    end_time = models.DateTimeField('脚本结束时间', blank=True, null=True)
    total_time = models.FloatField('执行脚本总耗时时间', blank=True, null=True)
    run_type = models.IntegerField('启动方式', default=0, null=True)
    '''
    run_type：
    0: 页面执行
    1：计划任务执行
    '''
    task_id = models.CharField('任务id', max_length=50, blank=True, null=True)
    '''
    filetransfer        文件传输
    bash               脚本执行
    job                 作业执行
    job_filetransfer    作业子任务 文件传输
    job_bash           作业子任务 脚本执行
    '''
    task_type = models.CharField('任务类型', max_length=50, blank=True, null=True)

    def task(self):
        if self.task_type.endswith('filetransfer'):
            return FileTransfer.objects.safe_get(id=self.task_id)
        if self.task_type.endswith('bash'):
            return RunScript.objects.safe_get(id=self.task_id)
        if self.task_type == 'job':
            return Job.objects.safe_get(id=self.task_id)
        return None

    def to_dict(self):
        """
        覆盖父类转换字典方法，添加关联实体task对象的字典
        :return:
        """
        task = self.task()
        result = super(self.__class__, self).to_dict()
        # 记录关联任务实例转换为字典
        if task:
            result['task'] = super(task.__class__, task).to_dict()
        else:
            result['task']= {}
        return result

    def __unicode__(self):
        return "TaskRecord<%s>" % self.name

    class Meta:
        verbose_name = '作业历史'
        permissions = (('view_taskrecord', '访问' + verbose_name),)


class CronJob(BaseModel):
    id = models.UUIDField('uuid', primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('定时任务名', max_length=200, blank=True, null=True)
    script_content = models.TextField('脚本内容', blank=True, null=True)
    cron_content = models.CharField('定时表达式', max_length=200, blank=True, null=True)
    server = models.CharField('目标主机', max_length=10000, blank=True, null=True)
    cron_creater = models.CharField('创建人', max_length=100, blank=True, null=True)
    cron_modified = models.CharField('最后修改人', max_length=100, blank=True, null=True)
    status = models.IntegerField('当前状态', default=0)
    '''
    0: 未启用
    1: 已启用
    '''

    class Meta:
        verbose_name = '计划任务'
        permissions = (('view_cronjob', '访问' + verbose_name),)
