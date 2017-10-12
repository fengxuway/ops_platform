# coding: utf-8


from django.db import models
from django.conf import settings
import datetime
import pytz


class BaseManager(models.Manager):
    def safe_get(self, *args, **kwargs):
        """
        安全获取唯一的数据，Model.objects.get()不抛出异常的版本，如果不存在或存在多条，则返回None
        :param args:
        :param kwargs:
        :return:
        """
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None
        except self.model.MultipleObjectsReturned:
            return None


class BaseModel(models.Model):
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)


    objects = BaseManager()

    def get_type(self):
        return self.__class__.__name__

    def to_dict(self):
        d = {}
        for _attr in self._meta.fields:
            attr = _attr.name
            try:
                val = getattr(self, attr)
            except Exception:
                d[attr] = None
                continue
            if attr == 'password':
                continue
            if val is None:
                d[attr] = None
            elif isinstance(val, datetime.datetime):
                # 转换时区（数据库存储UTC时间）
                val = val.replace(tzinfo=pytz.UTC).astimezone(pytz.timezone(settings.TIME_ZONE))
                d[attr] = val.strftime('%Y-%m-%d %H:%M')
            elif isinstance(val, datetime.date):
                d[attr] = val.strftime('%Y-%m-%d')
            elif isinstance(val, BaseModel):
                d[attr] = val.to_dict()
            else:
                d[attr] = getattr(self, attr)
        return d

    class Meta:
        abstract = True
