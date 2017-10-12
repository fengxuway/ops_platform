#!/usr/bin/env python
# coding:utf-8

from django import forms
'''
< QueryDict: {
                 'I18B': ['1'],
                 'hostnames_I14B[]': ['bj-ksy-v4-t2d-01', 'bj-ksy-v4-tchat-01', 'bj-ksy-v4-web-01'],
                 'vpc': ['509ffb8a-b6b6-495a-8f60-29e3345b960b'],
                 'I14B': ['3'],
                 'subnet': ['71f47b23-ca6c-47f9-b91d-c347c7992169'],
                 'region': ['cn-beijing-6'],
                 'hostnames_I18B[]': ['bj-ksy-v4-kf_master-01'],
                 'I14C': ['0'],
                 'hostnames_I18A[]': ['bj-ksy-v4-java-01', 'bj-ksy-v4-java-02'],
                 'I18A': ['2']} >
'''


class CreateECS(forms.Form):
    hostnames_I18B = forms.CheckboxSelectMultiple()
    hostnames_I18A = forms.CheckboxSelectMultiple()
    hostnames_I14B = forms.CheckboxSelectMultiple()
    hostnames_I14C = forms.CheckboxSelectMultiple()
    region = forms.CharField()
    vpc = forms.CharField()
    subnet = forms.CharField()

    # def clean_hostnames_I18B(self):
    #     return self.data.getlist('hostnames_I18B[]', [])
    #
    # def clean_hostnames_I18A(self):
    #     return self.data.getlist('hostnames_I18A[]', [])
    #
    # def clean_hostnames_I14B(self):
    #     return self.data.getlist('hostnames_I14B[]', [])
    #
    # def clean_hostnames_I14C(self):
    #     return self.data.getlist('hostnames_I14C[]', [])

def main():
    pass


if __name__ == '__main__':
    main()
