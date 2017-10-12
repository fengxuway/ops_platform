#!/usr/bin/python
# coding:utf-8
__author__ = 'Fengxu'
from django import forms


class FileForm(forms.Form):
    upload_file = forms.FileField()


class AddServer(forms.Form):
    id = forms.IntegerField(required=False)
    type = forms.CharField()
    name = forms.CharField(max_length=48)
    inner_ip = forms.CharField(required=False, max_length=16)
    outer_ip = forms.CharField(required=False, max_length=16)
    area = forms.CharField(max_length=20)
    user = forms.CharField(max_length=20, required=False)
    password = forms.CharField(max_length=40, required=False)
    port = forms.IntegerField(required=False)
    bandwidth = forms.CharField(max_length=40, required=False)
    monitor = forms.CharField(max_length=100, required=False)
    remark = forms.CharField(max_length=40, required=False)


class AddDomain(forms.Form):
    id = forms.IntegerField(required=False)
    type = forms.CharField()
    domain = forms.CharField(max_length=80)
    ip = forms.CharField(max_length=16)
    category = forms.IntegerField()
    remark = forms.CharField(max_length=40, required=False)


def main():
    pass


if __name__ == "__main__":
    main()
