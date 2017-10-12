# coding:utf-8
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from options.models import DataOption
import logging
from common.forms import PageData
import traceback
from options.forms import DataOptionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from common.permissions import *


log = logging.getLogger('django')


@login_required
@permission_required(VIEW_DATAOPTION)
def index(request):
    return render(request, 'options/index.html', locals())


@login_required
@permission_required(VIEW_DATAOPTION, raise_exception=True)
def page(request):
    log.info('searching option data...')
    dp = PageData(request.GET)
    category = request.GET.get('category', '')
    if dp.is_valid():
        page_info = dp.get_page_info()

        try:
            query = DataOption.objects.all()
            if category:
                query = query.filter(category=category)
            order = dp.get_sort_rule()
            order_col = order[0]
            if order[1] != 'asc':
                order_col = "-" + order[0]
            data = query.order_by(order_col)[page_info[0]:page_info[0]+page_info[1]]
            data = [x.to_dict() for x in data]
            length = query.count()
            mp = dp.get_data(data, length)
            log.info("search option data success. find: %s" % length)
            return JsonResponse(mp)
        except Exception:
            log.error('search get the ERROR: ' + traceback.format_exc())
            return JsonResponse({'result': False, 'message': 'search get the ERROR: \n'})
    return JsonResponse({'result': False, 'message': 'the Request params probably lose something.'})


@login_required
@permission_required(perm=(VIEW_DATAOPTION, ADD_DATAOPTION, CHANGE_DATAOPTION), raise_exception=True)
def add_data(request):
    if request.method == "POST":
        do = DataOptionForm(request.POST)
        if do.is_valid():
            data = do.cleaned_data
            if data['id']:
                # update
                DataOption.objects.filter(id=data['id']).update(
                    category=data['category'],
                    keyword=data['keyword'],
                    service_type=data['service_type'],
                    remark=data['remark']
                )
                log.info("Data Option update Sucess.")
                return JsonResponse({'result': True, 'message': '修改成功！'})
            else:
                # insert
                # 去除重复的keyword
                if DataOption.objects.filter(keyword__iexact=data['keyword'],
                                             category__iexact=data['category']).count() > 0:
                    return JsonResponse({'result': False, 'message': '已存在相同的数据！'})
                DataOption(
                    category=data['category'],
                    keyword=data['keyword'],
                    service_type=data['service_type'],
                    remark=data['remark']
                ).save()
                log.info("Data Option saved Sucess.")
                return JsonResponse({'result': True, 'message': '添加成功！'})
        else:
            log.error("Data Option submitted has missed params")
            return JsonResponse({'result': False, 'message': '请填写名称'})
    else:
        pass


@login_required
@permission_required(perm=(DELETE_DATAOPTION,), raise_exception=True)
def remove_data(request):
    do_id = request.POST.getlist("id[]", [])
    log.info("start Remove Server: " + str(do_id))
    if not do_id:
        log.error("Remove Server not appoint!")
        return JsonResponse({'result': False, 'message': '请输入要删除的Server ID'})

    try:
        DataOption.objects.filter(id__in=do_id).delete()
        log.info('Data option delete Sucess！' + str(do_id))
        return JsonResponse({'result': True, 'message': ''})
    except Exception as e:
        log.error("Data option Remove Failed! Caused by: \n" + traceback.format_exc())
        return JsonResponse({'result': False, 'message': '删除失败：' + e.message})


@login_required
@permission_required(VIEW_DATAOPTION)
def data_option(request):
    return render(request, 'options/data_option.html', locals())

