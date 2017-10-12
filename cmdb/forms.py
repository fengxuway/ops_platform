#!/usr/bin/python
# coding:utf-8
__author__ = 'Fengxu'
from django import forms


class FileForm(forms.Form):
    upload_file = forms.FileField()


class AddServer(forms.Form):
    id = forms.IntegerField(required=False)
    # name = forms.CharField(max_length=20)
    inner_ip = forms.CharField(required=False, max_length=16)
    outer_ip = forms.CharField(required=False, max_length=16)
    area = forms.CharField(max_length=40)
    user = forms.CharField(max_length=20)
    password = forms.CharField(max_length=40)
    port = forms.IntegerField(required=False)
    sn = forms.CharField(required=False)
    remark = forms.CharField(required=False)


class AddDomain(forms.Form):
    id = forms.IntegerField(required=False)
    type = forms.CharField()
    domain = forms.CharField(max_length=80)
    ip = forms.CharField(max_length=16)
    category = forms.IntegerField()
    remark = forms.CharField(max_length=40, required=False)


class AddServerApiForm(forms.Form):
    innerIp = forms.CharField(max_length=40, required=False)
    publicIp = forms.CharField(max_length=40, required=False)
    user = forms.CharField(max_length=40, required=False)
    port = forms.IntegerField(required=False)
    kw = forms.CharField(required=False)


def main():
    pass


if __name__ == "__main__":
    main()
