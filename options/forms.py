#!/usr/bin/python
# coding:utf-8
from django import forms


class DataOptionForm(forms.Form):
    id = forms.IntegerField(required=False)
    keyword = forms.CharField(max_length=20, required=True)
    service_type = forms.CharField(max_length=50, required=False)
    category = forms.CharField(max_length=12, required=True)
    remark = forms.CharField(max_length=40, required=False)


def main():
    pass


if __name__ == "__main__":
    main()
