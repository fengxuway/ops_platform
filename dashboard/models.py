#!/usr/bin/env python
# coding=utf-8


from django.db import models
from common.models import BaseModel


class SiteRecord(BaseModel):
    last_time = models.DateTimeField('最后获取时间', null=False)
    data = models.CharField('数据表的json字符串数据', null=False, max_length=1000)
    hostname = models.CharField('数据来源的主机名', null=False, default='', max_length=100)