# coding: utf-8


from django.db import models
from common.models import BaseModel, BaseManager
import datetime
import time
from common.util.mysql_util import connect
import logging
from common.util import des
from common.util import id_creater
import traceback
from common.util.des import encrypt
from django.db.models import Q
from common.util.id_creater import server_id


log = logging.getLogger('django')


class Server(BaseModel):
    """Server Manage Table"""
    server_id = models.CharField('ServerID', max_length=20, unique=True, null=True)
    category = models.CharField('Server类别', max_length=12, blank=True, null=True)
    name = models.CharField('名称', max_length=48, blank=True, null=True)
    hostname = models.CharField('主机名', max_length=20, blank=True, null=True)
    inner_ip = models.CharField('内网IP', max_length=16, blank=True, null=True)
    outer_ip = models.CharField('公网IP', max_length=16, blank=True, null=True)
    user = models.CharField('用户', max_length=20, blank=True, null=True)
    password = models.CharField('密码', max_length=100, blank=True, null=True)
    port = models.IntegerField('端口', default=22, blank=False)
    os = models.CharField('操作系统', max_length=20, blank=True, null=True)
    memory = models.IntegerField('内存（单位MB）', default=0, null=True)
    memory_free = models.IntegerField('剩余内存（单位MB）', default=0, null=True)
    bandwidth = models.CharField('带宽', max_length=20, blank=True, null=True)
    cpu = models.CharField('CPU', max_length=200, blank=True, null=True)
    domain = models.CharField('域名', max_length=48, blank=True, null=True)
    rack = models.CharField('机架', max_length=40, blank=True, null=True)
    area = models.CharField('机房', max_length=20, blank=True, null=True)
    monitor = models.CharField('监控', max_length=100, blank=True, null=True)
    remark = models.CharField('备注', max_length=40, null=True, default="")
    connect = models.IntegerField('连接状态【0未连接，1正在连接，2已连接，-1连接失败】', default=0)
    connect_log = models.TextField('连接日志', null=True)
    ansible_host = models.CharField('可连接到主机的IP，供ansible使用', max_length=100, null=True, blank=True)
    state = models.IntegerField('服务器状态', default=0)

    def __unicode__(self):
        return "Server<%s>" % self.hostname

    def insert(self, enc=False):
        try:
            if not self.port:
                self.port = 22
            self.port = int(self.port)
            if not self.server_id:
                self.server_id = server_id()
        except ValueError:
            self.port = 22
        q_filter = Q(server_id=self.server_id)
        if self.inner_ip:
            q_filter |= Q(inner_ip=self.inner_ip)
        if self.outer_ip:
            q_filter |= Q(outer_ip=self.outer_ip)
        if enc:
            self.password = encrypt(self.password) if self.password else ""
        if Server.objects.filter(q_filter).count() == 0:
            self.save()
            return True
        return False

    class Meta:
        verbose_name = 'Server管理'
        permissions = (("view_server", "访问服务器"),)


class DomainManager(BaseManager):
    """
    Domain manager class
    """
    def page_search_data(self, page_start, page_size, orderby='domain', order_type='asc', kw="", area="", ip_category=2):
        """
        Domain get data by searching keyword and separate page info.
        :param page_start: separate page start record number
        :param page_size: the record number per page
        :param orderby: which column for order
        :param order_type: how to order (asc or desc)
        :param kw: search keyword for domain/ip/area/hostname and so oon
        :param area: search jifang info
        :param ip_category: the type of IP address
        :return: the tuple of searched data and total count: (data, length)
        """

        sql = " from server_domain d left join server_server s " \
              " on ( d.ip=s.inner_ip or d.ip=s.outer_ip ) where 1=1 "
        params = []
        if kw:
            sql += " and ( d.domain like %s or d.ip like %s " \
                   " or s.hostname like %s or s.area like %s ) "
            kw = "%" + kw + "%"
            params.extend([kw] * 4)
        if area:
            sql += " and s.area like %s "
            params.append("%" + area + "%")
        if ip_category != 2:
            sql += " and d.category=%s "
            params.append(str(ip_category))
        if orderby and order_type:
            sql += " order by %s %s "
            params.extend([orderby, order_type])
        length_sql = "select count(d.id) " + sql
        sql_data = "select d.* " + sql
        log.info("SQL for Count: " + length_sql % tuple(params))
        log.info("SQL for Data: " + sql_data % tuple(params))

        with connect() as cursor:
            cursor.execute(length_sql, params)
            count_row = cursor.fetchone()
            length = count_row[0]
        data = self.raw(sql_data, params)[page_start:page_start + page_size]
        log.info("searched Domain: " + str(data) + " size: " + str(length))
        return data, length

    def exists(self, category, ip, domain):
        """
        判断是否存在指定IP或指定域名的映射。
        :param category: IP类型 0内网，1外网
        :param ip: IP地址
        :param domain: 域名
        :return: 如果IP和域名存在其一，则返回True
        """
        if self.filter(category=category, ip=ip).count() > 0:
            return True
        if self.filter(domain=domain).count() > 0:
            return True
        return False


class Domain(BaseModel):
    domain = models.CharField('域名', max_length=80, blank=True, null=True)
    ip = models.CharField('IP地址', max_length=16, blank=True, null=True)
    category = models.IntegerField('IP类型【0内网IP，1外网IP】')
    remark = models.CharField('备注', max_length=40, null=False, default="")

    objects = DomainManager()

    def __unicode__(self):
        return "Domain<%s>" % self.domain

    def to_dict(self):
        if self.category == 0:
            servers = Server.objects.filter(inner_ip=self.ip)
        else:
            servers = Server.objects.filter(outer_ip=self.ip)
        if servers:
            server = servers[0].to_dict()
        else:
            server = None
        return dict(
            id=self.id,
            domain=self.domain,
            ip=self.ip,
            category=self.category,
            remark=self.remark,
            server=server
        )

    class Meta:
        verbose_name = '域名管理'
        permissions = (("view_domain", "访问域名映射"),)
