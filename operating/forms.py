#!/usr/bin/python
# coding:utf-8
from django import forms



class FileForm(forms.Form):
    upload_file = forms.FileField()


class RunScriptForm(forms.Form):
    # name = forms.CharField(required=False)
    user = forms.CharField(required=False)
    server = forms.CharField()
    script_content = forms.CharField()
    script_args = forms.CharField(required=False)

    def clean_script_content(self):
        return self.cleaned_data['script_content'].replace('\r', '')


class FileTransferForm(forms.Form):
    # name = forms.CharField()
    file_path = forms.CharField()
    dest = forms.CharField()
    user = forms.CharField()
    server_ids = forms.CharField()

    def clean_server_ids(self):
        return self.data.getlist('server_ids', [])

    def clean_file_path(self):
        return self.data.getlist('file_path', [])


class CronjobForm(forms.Form):
    name = forms.CharField()
    cron_creater = forms.CharField(required=False)
    server = forms.CharField()
    script_content = forms.CharField()
    cron_content = forms.CharField()


def main():
    pass


if __name__ == "__main__":
    main()
