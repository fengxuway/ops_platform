#!/usr/bin/python
# coding:utf-8
from django import template
import datetime
from options.models import DataOption
__author__ = 'Fengxu'

register = template.Library()


@register.filter(name='split')
def split(value, arg):
    return value.split(arg)


@register.tag(name="data_option")
def do_get_data_options(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, category = token.split_contents()
    except ValueError:
        msg = '%r tag requires a single argument' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    return DataNode(category[1:-1])


class DataNode(template.Node):
    def __init__(self, category):
        self.category = str(category)

    def render(self, context):
        if self.category == '_category':
            # get all categorys
            datas = DataOption.objects.values('category').distinct()
            html = ''
            for data in datas:
                html += '<option value="%s">%s</option>' % (data['category'], data['category'])
            return html
        else:
            datas = DataOption.objects.filter(category=self.category)
            html = ''
            for data in datas:
                html += '<option value="%s">%s</option>' % (data.keyword, data.keyword)
            return html


def main():
    pass


if __name__ == "__main__":
    main()
