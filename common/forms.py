#!/usr/bin/python
# coding:utf-8
__author__ = 'Fengxu'

from django import forms


class PageData(object):
    """
    Clean up the separate page Form's data. Need data from request.GET or request.POST.
    """
    class PageDataForm(forms.Form):
        sEcho = forms.IntegerField()
        iColumns = forms.IntegerField()
        iDisplayStart = forms.IntegerField()
        iDisplayLength = forms.IntegerField()
        iSortCol_0 = forms.IntegerField()
        sSortDir_0 = forms.CharField()
        iSortingCols = forms.IntegerField()

    def __init__(self, post_data):
        self.data_page = self.PageDataForm(post_data)
        self.valid = self.data_page.is_valid()
        if self.valid:
            form_data = self.data_page.cleaned_data
            self.page_size = form_data['iDisplayLength']
            self.page_start = form_data['iDisplayStart']
            self.sEcho = form_data['sEcho']
            self.cols = form_data['iColumns']
            self.sort_col_num = form_data['iSortCol_0']
            self.sort_rule = form_data['sSortDir_0']
            self.sort_col = post_data['mDataProp_' + str(self.sort_col_num)]

        else:
            self.page_size = self.page_start = self.cols = sort_col_num = 0
            self.sEcho = self.sort_col = self.sort_rule = ""

    def is_valid(self):
        """
        the data from request if or not valid( depend on class DataForm
        :return:
        """
        return self.valid

    def get_page_info(self):
        """
        get separate page's info, what record start, and what one page display
        :return: tuple: (page_start, page_size)
        """
        if self.valid:
            return self.page_start, self.page_size
        return None

    def get_sort_rule(self):
        """
        get how to sort the list
        :return:tuple:(sort_row's name, sort_rule"asc or desc")
        """
        if self.valid:
            return self.sort_col, self.sort_rule
        return None

    def get_data(self, data, total):
        """
        generate the dict data for JqueryDataTable plugin
        :param data:
        :param total:
        :return:
        """
        mp = dict()
        if self.valid:
            mp['aaData'] = data
            mp['iTotalRecords'] = total
            mp['iTotalDisplayRecords'] = total
            mp['sEcho'] = self.sEcho

        return mp


def main():
    pass


if __name__ == "__main__":
    main()
