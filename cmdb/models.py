# coding: utf-8

from django.db import models
from common.models import BaseManager, BaseModel
from django.db.models import Q
from common.util.des import encrypt


class ServerGroup(BaseModel):
    name = models.CharField('主机组名', max_length=40, null=False)
    count = models.IntegerField('主机数量', default=0)
    remark = models.CharField('备注', max_length=100, null=True, blank=True)
    label = models.IntegerField('分类0自动生成, 1手动添加', default=0)

    def __unicode__(self):
        return "ServerGroup<%s>" % self.name

    class Meta:
        verbose_name = '资产组管理'


class ServerInfo(BaseModel):
    RegionId = models.CharField('地域', max_length=40, null=False)
    ZoneId = models.CharField('可用区', max_length=40, null=True, default='')
    InstanceId = models.CharField('实例的编号', max_length=40, null=False, unique=True)
    InstanceName = models.CharField('实例名称', max_length=40, null=False)
    InstanceType = models.CharField('类型', max_length=40, null=True, blank=True)    # ecs
    PublicIpAddress = models.CharField('公网IP', max_length=80, null=False)
    InnerIpAddress = models.CharField('内网IP', max_length=80, null=False)
    IpType = models.CharField('IP地址网络类型', max_length=12, default='default')
    # aliyun :Running Starting Stopping Stopped
    # ksyun: 有效值: active | building | paused | suspended | stopped | rescued | resized | soft-delete | deleted | deleting | error | scheduling |
        # block_device_mapping | networking | spawning | image_snapshot | image_backup | updating_password | resize_prep | resize_migrating |
        # resize_migrated | resize_finish | resize_finish | resize_reverting | resize_confirming | migrating | rebooting | rebooting_hard | pausing |
        # unpausing | suspending | resuming | stopping | starting | powering-off | powering-on | rescuing | unrescuing | rebuilding |
        # rebuild_block_device_mapping | rebuild_spawning | deleting
    Status = models.CharField('状态', max_length=40, null=False)
    Cpu = models.IntegerField('CPU数量', default=0)
    Cpu_info = models.CharField('CPU信息', max_length=50, blank=True, null=True)
    Memory = models.IntegerField('内存大小GB', default=0)
    DiskSize = models.IntegerField('硬盘大小GB', default=0)
    DiskType = models.CharField('硬盘类型 SATA | SSD | EFFICIENCY(混合)', max_length=50, blank=True, default="SATA", null=True)
    InternetMaxBandwidthOut = models.IntegerField('带宽', default=0)
    InternetMaxBandwidthIn = models.IntegerField('带宽下载', default=0)
    ansible_host = models.CharField('可连接到主机的IP，供ansible使用', max_length=100, null=True, blank=True)
    os = models.CharField('操作系统', max_length=50, blank=True, null=True)
    os_release = models.CharField('操作系统发行版本', max_length=50, blank=True, null=True)
    os_version = models.CharField('操作系统版本', max_length=50, blank=True, null=True)
    enabled = models.IntegerField('状态值，是否可用。默认为可用', default=0)
    """
    0:可用
    1:不可用
    """
    group = models.ManyToManyField(ServerGroup, db_constraint=False)
    sys_bits = models.CharField('操作系统位数', max_length=20, blank=True, null=True)

    # hand input info in form
    server_location = models.CharField('服务器存放地点', max_length=50, blank=True, null=True)
    sn = models.CharField('服务器sn号', max_length=50, blank=True, null=True)
    user = models.CharField('用户', max_length=50, blank=True, null=True)
    pwd = models.CharField('密码', max_length=50, blank=True, null=True)
    port = models.IntegerField('端口号', blank=False, default=22)
    remark = models.CharField('备注', max_length=200, blank=True, null=True)
    connect_log = models.TextField('连接日志', null=True)
    connect = models.IntegerField('连接状态【0未连接，1正在连接，2已连接，-1连接失败】', default=0)

    def to_dict(self):
        server_dict = super(self.__class__, self).to_dict()
        server_dict['groups'] = [g.to_dict() for g in self.group.all()]
        return server_dict

    def insert(self, enc=False):
        if not self.port:
            self.port = 8022
        self.port = int(self.port)
        if self.InnerIpAddress and self.PublicIpAddress:
            q_filter = Q(InnerIpAddress__contains=self.InnerIpAddress) | Q(PublicIpAddress__contains=self.PublicIpAddress)
        elif self.PublicIpAddress:
            q_filter = Q(PublicIpAddress__contains=self.PublicIpAddress)
        elif self.InnerIpAddress:
            q_filter = Q(InnerIpAddress__contains=self.InnerIpAddress)
        if enc:
            self.pwd = encrypt(self.pwd) if self.pwd else ""
        if ServerInfo.objects.filter(q_filter).count() == 0:
            self.save()
            return True
        return False

    def __unicode__(self):
        return "ServerInfo<%d, %s>" % (self.id, self.InstanceName)

    class Meta:
        verbose_name = 'CMDB-Server管理'


class KsyEipManager(BaseManager):
    def insert(self, data_dict):
        # data_dict = {
        #     "PublicIp": "120.92.77.179",
        #     "AllocationId": "fe3d61af-7964-4ed0-a061-06aea4b8ecd0",
        #     "State": "disassociate",
        #     "LineId": "5fc2595f-1bfd-481b-bf64-2d08f116d800",
        #     "BandWidth": 5,
        #     "CreateTime": "2017-01-05 15:27:22"
        # }
        for key in ['NetworkInterfaceId', 'InstanceType', 'InstanceId', 'InternetGatewayId']:
            if key not in data_dict:
                data_dict[key] = ''
        eips = self.filter(AllocationId=data_dict['AllocationId'])
        if not eips:
            eip = KsyEip()
        else:
            eip = eips[0]
        eip.AllocationId = data_dict['AllocationId']
        eip.PublicIp = data_dict['PublicIp']
        eip.State = data_dict['State']
        eip.LineId = data_dict['LineId']
        eip.BandWidth = data_dict['BandWidth']
        eip.CreateTime = data_dict['CreateTime']
        # 金山云API可选项
        eip.NetworkInterfaceId = data_dict['NetworkInterfaceId']
        eip.InstanceType = data_dict['InstanceType']
        eip.InstanceId = ServerInfo.objects.safe_get(InstanceId=data_dict['InstanceId'])
        eip.InternetGatewayId = data_dict['InternetGatewayId']
        eip.save()



class KsyEip(BaseModel):
    '''
    CREATE TABLE `ntdeploy`.`cmdb_ksyeip` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `PublicIp` VARCHAR(16) NOT NULL,
      `AllocationId` VARCHAR(40) NOT NULL,
      `State` VARCHAR(16) NOT NULL,
      `LineId` VARCHAR(40) NOT NULL,
      `NetworkInterfaceId` VARCHAR(40) NULL,
      `BandWidth` INT NULL DEFAULT 0,
      `InstanceType` VARCHAR(40) NULL,
      `InstanceId` VARCHAR(40) NULL,
      `InternetGatewayId` VARCHAR(40) NULL,
      `CreateTime` VARCHAR(40) NULL,
      `create_time` DATETIME NOT NULL,
      `update_time` DATETIME NOT NULL
      PRIMARY KEY (`id`));
    '''
    PublicIp = models.CharField('弹性IP地址', max_length=16, null=False, blank=False)
    AllocationId = models.CharField('分配ID', max_length=40, null=False, blank=False)
    State = models.CharField('EIP状态(associate/disassociate)', max_length=40, null=False, blank=False)
    LineId = models.CharField('链路ID', max_length=40, null=False, blank=False)
    NetworkInterfaceId = models.CharField('网卡ID', max_length=40, null=False, blank=True, default='')
    BandWidth = models.IntegerField('带宽', null=False, default=0)
    InstanceType = models.CharField('EIP类型(Ipfwd/Slb)', max_length=40, null=False, default=0)
    # InstanceId = models.CharField('EIP实例ID', max_length=40, null=False, blank=True, default='')
    InstanceId = models.OneToOneField(ServerInfo, to_field='InstanceId', db_constraint=False)
    InternetGatewayId = models.CharField('网关ID', max_length=40, null=False, blank=True, default='')
    CreateTime = models.CharField('创建时间', max_length=40, null=False, blank=True, default='')

    objects = KsyEipManager()

