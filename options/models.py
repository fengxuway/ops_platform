# coding:utf-8

from common.models import BaseModel
from django.db import models


class DataOption(BaseModel):
    category = models.CharField('分类', max_length=12, null=True, blank=True)
    keyword = models.CharField('关键字', max_length=20, null=True, blank=True)
    service_type = models.CharField('服务类型（服务类别专属）', max_length=50, default='')
    remark = models.CharField('备注', max_length=40, null=True, blank=True)

    def insert(self):
        if self.category and self.keyword:
            if DataOption.objects.filter(category=self.category, keyword__iexact=self.keyword).count() == 0:
                self.save()
                return True
        return False

    class Meta:
        verbose_name = '数据字典'
        permissions = (("view_dataoption", "访问数据字典"),)