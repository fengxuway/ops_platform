from django.shortcuts import render
from django.http import JsonResponse, HttpResponse


from kscore.session import get_session
from django.conf import settings
import traceback
import logging
import time
import json
from grid.forms import CreateECS
from grid.logic import init_ecs, delay_test, test_ecs, create_ecs
from celery.result import AsyncResult
ACCESS_KEY_ID = settings.ACCESS_KEY_ID
SECRET_ACCESS_KEY = settings.SECRET_ACCESS_KEY


log = logging.getLogger('django')


def mytask():
    print("start task")
    time.sleep(10)
    print("finish task")

def newgrid(request):
    """
    进入新建Grid主机页面
    post请求创建服务器
    :param request: 
    :return: 
    """
    if request.method == 'GET':
        return render(request, 'grid/index.html', context=locals())
    else:
        try:
            form_data = json.loads(request.body.decode("utf-8"))
            if 'vpc' in form_data and 'subnet' in form_data and 'region' in form_data \
                and 'hostnames_I14B' in form_data and 'hostnames_I14C' in form_data \
                and (form_data['hostnames_I18B'] or form_data['hostnames_I18A']
                     or form_data['hostnames_I14B'] or form_data['hostnames_I14C']):
            # form = CreateECS(form_data)
            # if form.is_valid():
            #     data = form.cleaned_data
                data = form_data
                log.info("creating...", data)

                task = create_ecs.delay(data)
                return JsonResponse({"result": True, "message": "Creating ECS....", "task_id": task.id})

            else:
                log.error("表单异常! ")
                return JsonResponse({"result": False, "message": "Form error, Please check your Input."})
        except Exception as e:
            traceback.print_exc()


def retry_init(request):
    """
    重试初始化进程
    :param request: body: [{'InstanceName': 'bj-ksy-vn-java-01', 'InstanceId': '218edaab-3f0f-4c5f-8775-54c961779e99'},] 
    :return: 
    """
    try:
        data = json.loads(request.body.decode("UTF-8"))
        _task = init_ecs.delay(data)
        return JsonResponse({"result": True, "message": "初始化中", "task_id": _task.id})
    except Exception as e:
        log.error(traceback.format_exc())
        return JsonResponse({"result": False, "message": "执行失败：" + traceback.format_exc()})


def task(request, task_id):
    _task = AsyncResult(task_id)
    if _task:
        print({"result": True, "message": _task.result, "status": _task.status})
        return JsonResponse({"result": True, "message": _task.result, "status": _task.status})
    else:
        return JsonResponse({"result": False, "message": "Task Not found"})



def test(request):
    data = [{'InstanceId': '622a2477-4f13-4497-be9c-80e50f03e27b', 'InstanceName': 'bj-ksy-vtest-java-01'}, {'InstanceId': 'ff53cfa8-ff6f-4f6a-800a-2a722c1ec7c9', 'InstanceName': 'bj-ksy-vtest-t2d-01'}, {'InstanceId': 'f748e3ba-457b-4a3d-99ae-0a441f7b918b', 'InstanceName': 'bj-ksy-vtest-tchat-01'}]

    r = init_ecs.delay(data, {'region': 'cn-beijing-6'})
    print(r)
    return HttpResponse("Init Server...")

def vpcs(request, region):
    """
    查询指定区域的所有vpc
    :param request: 
    :param region: 
    :return: 
    """
    s = get_session()
    client_vpc = s.create_client("vpc", region, use_ssl=False, ks_access_key_id=ACCESS_KEY_ID,
                                 ks_secret_access_key=SECRET_ACCESS_KEY)
    return JsonResponse(client_vpc.describe_vpcs())


def subnets(request, region, vpc_id):
    """
    查询指定区域、指定vpc的所有子网
    :param request: 
    :param region: 
    :param vpc_id: 
    :return: 
    """
    try:
        s = get_session()
        client_vpc = s.create_client("vpc", region, use_ssl=False, ks_access_key_id=ACCESS_KEY_ID,
                                     ks_secret_access_key=SECRET_ACCESS_KEY)
        subnets = {"SubnetSet": []}
        for i in client_vpc.describe_subnets()['SubnetSet']:
            if i['VpcId'] == vpc_id:
                subnets['SubnetSet'].append(i)

        return JsonResponse(subnets)
    except Exception as e:
        traceback.print_exc()