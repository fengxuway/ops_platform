#!/usr/bin/env python
# coding:utf-8
import time
from celery.task import task
from kscore.session import get_session
from django.conf import settings
import logging
import os
import traceback
from service.logic import run_task


log = logging.getLogger('django')


@task
def delay_test(a):
    print("start task...")
    time.sleep(15)
    print("end task", a)
    return {'a':'b', 'c':['d']}

@task
def test_ecs():
    r = run_task(['172.66.110.12 ansible_user=root ansible_port=22 ansible_ssh_pass=__password__'], 'setup')
    print(r)
    return r

@task
def create_ecs(form_data):
    try:
        client = get_session().create_client("kec", form_data['region'], use_ssl=False, ks_access_key_id=settings.ACCESS_KEY_ID,
                                 ks_secret_access_key=settings.SECRET_ACCESS_KEY)
        results = []
        for hostname in form_data['hostnames_I18B']:
            run_result = client.run_instances(ImageId='cb7a02d2-a6e2-4bc4-a3a0-5ee8b131a451',
                                              InstanceType='I1.8B',
                                              DataDiskGb=500,
                                              MaxCount=1,
                                              MinCount=1,
                                              InstancePassword='__password__',
                                              SubnetId=form_data['subnet'],
                                              SecurityGroupId='1f66de4c-a5c2-4e94-a416-58ec0b5a5a21',
                                              InstanceName=hostname,
                                              ChargeType='Daily'
                                              )

            log.info("I18B: ", run_result)
            results.extend(run_result['InstancesSet'])
        for hostname in form_data['hostnames_I18A']:
            run_result = client.run_instances(ImageId='cb7a02d2-a6e2-4bc4-a3a0-5ee8b131a451',
                                              InstanceType='I1.8A',
                                              DataDiskGb=200,
                                              MaxCount=1,
                                              MinCount=1,
                                              InstancePassword='__password__',
                                              SubnetId=form_data['subnet'],
                                              SecurityGroupId='1f66de4c-a5c2-4e94-a416-58ec0b5a5a21',
                                              InstanceName=hostname,
                                              ChargeType='Daily'
                                              )
            log.info("I18A: ", run_result)
            results.extend(run_result['InstancesSet'])
        for hostname in form_data['hostnames_I14B']:
            run_result = client.run_instances(ImageId='cb7a02d2-a6e2-4bc4-a3a0-5ee8b131a451',
                                              InstanceType='I1.4B',
                                              DataDiskGb=200,
                                              MaxCount=1,
                                              MinCount=1,
                                              InstancePassword='__password__',
                                              SubnetId=form_data['subnet'],
                                              SecurityGroupId='1f66de4c-a5c2-4e94-a416-58ec0b5a5a21',
                                              InstanceName=hostname,
                                              ChargeType='Daily'
                                              )
            log.info("I14B: ", run_result)
            results.extend(run_result['InstancesSet'])
        for hostname in form_data['hostnames_I14C']:
            run_result = client.run_instances(ImageId='cb7a02d2-a6e2-4bc4-a3a0-5ee8b131a451',
                                              InstanceType='I1.4C',
                                              DataDiskGb=200,
                                              MaxCount=1,
                                              MinCount=1,
                                              InstancePassword='__password__',
                                              SubnetId=form_data['subnet'],
                                              SecurityGroupId='1f66de4c-a5c2-4e94-a416-58ec0b5a5a21',
                                              InstanceName=hostname,
                                              ChargeType='Daily'
                                              )
            print("I14C: ", run_result)
            results.extend(run_result['InstancesSet'])
        log.info("ECS创建成功！")
        log.info(results)
        print(results)
        waiting_ecs(results, form_data)
        print(results)
        init_task = init_ecs.delay(results)
        return results, init_task.id
    except Exception as e:
        traceback.print_exc()

def waiting_ecs(ecs_list, form_data):
    """
    等待机器running，返回ID，内网IP等信息
    :param ecs_list: [{InstanceId, InstanceName, PrivateId, PublicId}...]
    :param form_data: 表单数据
    :return: [{InstanceId, InstanceName, PrivateId, PublicId}...] 直接修改ecs_list参数，不返回任何值
    """
    print("start ansible")
    client = get_session().create_client("kec", form_data['region'], use_ssl=False,
                                         ks_access_key_id=settings.ACCESS_KEY_ID,
                                         ks_secret_access_key=settings.SECRET_ACCESS_KEY)
    instances_args = {}
    for i in range(0, len(ecs_list)):
        instances_args['InstanceId.' + str(i + 1)] = ecs_list[i]['InstanceId']
        print('\tadd arg: ', 'InstanceId.' + str(i + 1), ecs_list[i]['InstanceId'])
    print("args: ", instances_args)
    for i in range(0, 60):
        time.sleep(5)
        print("fetching instances")
        status = client.describe_instances(**instances_args)
        print(status)
        log.info("hhhhh::", status)
        try:
            # str_status = str(status)
            # 是否继续等待的标志，如果状态有不为active的将继续循环等待
            loop_flag = False
            for _st in status['InstancesSet']:
                if 'InstanceState' in _st and 'Name' in _st['InstanceState'] \
                        and _st['InstanceState']['Name'] == 'active' and 'PrivateIpAddress' in _st:
                    continue
                else:
                    loop_flag = True
                    break
            if loop_flag:
                continue

            # if str_status and 'scheduling' not in str_status and 'spawning' not in str_status:
                # 将内网IP地址写入ecs_list对应的实例信息中
            for _instance_detail in status['InstancesSet']:
                for _instance_data in ecs_list:
                    if _instance_data['InstanceId'] == _instance_detail['InstanceId']:
                        _instance_data['PrivateIp'] = _instance_detail['PrivateIpAddress']
                        break
            break
        except Exception as e:
            traceback.print_exc()
    else:
        # 150 秒内 创建的机器仍有调度中的机器
        print("Create ECS ERROR, has scheduling status.")
    print("bind EIP to kf_master starting...")
    for instance_detail in ecs_list:
        if 'kf_master' in instance_detail['InstanceName']:
            kf_master = client.describe_instances(**{"InstanceId.1": instance_detail['InstanceId']})
            print("即将绑定EIP到kf_master，主机信息：", kf_master)
            if len(kf_master['InstancesSet']) == 0:
                print("不存在kf_master主机！")
                continue
            try:
                eip_client = get_session().create_client("eip", form_data['region'], use_ssl=False,
                                                         ks_access_key_id=settings.ACCESS_KEY_ID,
                                                         ks_secret_access_key=settings.SECRET_ACCESS_KEY)
                # 链路ID 对应于BGP， 使用eip_client.describe_addresses()查询
                eip = eip_client.allocate_address(ChargeType="Daily", BandWidth=50,
                                                  LineId='5fc2595f-1bfd-481b-bf64-2d08f116d800')
                # eip格式：{'PublicIp': '120.92.18.69', 'RequestId': '49363671-fa53-4c98-a286-eb3c5605f710', 'AllocationId': '0395cf2e-f26d-46c4-826d-c23002b59158'}
                print("创建EIP成功：", eip)
                print("正在绑定EIP：AllocationId=%s, InstanceType=%s, InstanceId=%s, NetworkInterfaceId=%s"
                      % (eip['AllocationId'], 'Ipfwd', kf_master['InstancesSet'][0]['InstanceId'],
                         kf_master['InstancesSet'][0]['NetworkInterfaceSet'][0]['NetworkInterfaceId']))
                eip_result = eip_client.associate_address(AllocationId=eip['AllocationId'], InstanceType='Ipfwd',
                                                          InstanceId=kf_master['InstancesSet'][0]['InstanceId'],
                                                          NetworkInterfaceId=
                                                          kf_master['InstancesSet'][0]['NetworkInterfaceSet'][0][
                                                              'NetworkInterfaceId'])
                # eip_result格式：{'RequestId': 'bfc3c418-222d-4e0a-b16e-e276545a350a', 'Return': True}
                print("绑定EIP结果：", eip_result)
                if eip_result['Return']:
                    print("绑定成功")
                    instance_detail['PublicIp'] = eip['PublicIp']
                else:
                    print("绑定失败！")
            except Exception as e:
                traceback.print_exc()
                # print(client.allocate_address(ChargeType="Daily", BandWidth=50, LineId='5fc2595f-1bfd-481b-bf64-2d08f116d800'))
                # {'AllocationId': '478a2f0b-5dfb-404d-bba8-0120787e93ee', 'PublicIp': '120.92.93.112', 'RequestId': '7b750f99-08d9-47e8-97f4-87de4d9ffd64'}

    print("bind EIP to kf_master success")

@task
def init_ecs(ecs_list):
    '''
    等待机器创建完毕运行时，使用ansible执行ksyinit脚本
    :param ecs_list: [{'InstanceName': 'bj-ksy-vn-java-01', 'InstanceId': '218edaab-3f0f-4c5f-8775-54c961779e99'},]
    :param form_data: 提交的表单数据，以方便在需要区域、VPC等信息时获取
    :return: 
    '''
    try:

        # 搜索指定实例ID列表的方式：
        # client.describe_instances(**{"InstanceId.1": "xxxxx"})
        # s = get_session()
        # client = get_session().create_client("kec", form_data['region'], use_ssl=False,
        #                                      ks_access_key_id=settings.ACCESS_KEY_ID,
        #                                      ks_secret_access_key=settings.SECRET_ACCESS_KEY)
        # client = s.create_client("kec", 'cn-beijing-6', use_ssl=False, ks_access_key_id=settings.ACCESS_KEY_ID,
        #                          ks_secret_access_key=settings.SECRET_ACCESS_KEY)

        print("start execute ksyinit")
        ansible_hosts = []
        for instance in ecs_list:
            if 'PrivateIp' in instance:
                # if instance['PrivateIpAddress'] == '172.66.110.12':
                #     ansible_hosts.append('%s ansible_user=root ansible_port=22 ansible_ssh_pass=__password__' % '172.66.110.122')
                # else:
                ansible_hosts.append('%s ansible_user=root ansible_port=22 ansible_ssh_pass=__password__' % instance['PrivateIp'])
            else:
                log.error("Instance's Private Ip Address Not Found!", instance)
        print("ansible_hosts: ", ansible_hosts)

        for _ in range(0, 24):
            print("开始测试ansible连通性 第 %d 次" % (_+1))
            ping_result = run_task(ansible_hosts, 'ping')
            print("------------------------------------------------------------------")
            # {'172.66.110.12': {'status': 'ok', 'result': {'_ansible_parsed': True, '_ansible_no_log': False, 'ping': 'pong', 'invocation': {'module_name': 'ping', 'module_args': {'data': None}}, 'changed': False}}}
            print(ping_result)
            ping_flag = True
            for ip, result in ping_result.items():
                # {'172.66.110.24':
                # {'result': {'msg': 'Failed to connect to the host via ssh: ssh: connect to host 172.66.110.24 port 22: Operation timed out\r\n', 'changed': False, 'unreachable': True},
                # 'status': 'unreachable'}, '172.66.110.6': {'result': {'msg': 'Failed to connect to the host via ssh: ssh: connect to host 172.66.110.6 port 22: Operation timed out\r\n', 'changed': False, 'unreachable': True}, 'status': 'unreachable'}, '172.66.110.25': {'result': {'msg': 'Failed to connect to the host via ssh: ssh: connect to host 172.66.110.25 port 22: Operation timed out\r\n', 'changed': False, 'unreachable': True}, 'status': 'unreachable'}}
                if result['status'] == 'ok' and result['result']['ping'] == 'pong':
                    continue
                else:
                    print("ERROR: ", ping_result)
                    ping_flag = False
                    break
            else:
                print("ansible连接成功！")
                break
            if not ping_flag:
                print("ansible连接失败，等待重试。。。")
                time.sleep(10)
                continue
        else:
            # 未能break，表示ansible连接失败，直接返回ping的结果
            for ip, results in ping_result.items():
                for _instance_data in ecs_list:
                    if 'PrivateIp' in _instance_data and _instance_data['PrivateIp'] == ip:
                        _instance_data['init_result'] = results
            return ecs_list

        print("======================开始执行init任务==============================")
        init_result = run_task(ansible_hosts, 'script', os.path.join(settings.BASE_DIR, 'scripts/ksy_init.sh'))
        # init_result = run_task(ansible_hosts, 'script', os.path.join(settings.BASE_DIR, 'scripts/hostname'))
        # init_result = run_task(ansible_hosts, 'setup')
        # log.info(init_result)
        print("------------------------------------------------------------------")
        print(init_result)
        print("==================================================================")
        '''
        {'172.66.110.122': {'status': 'unreachable', 'result': 
            {'changed': False, 'unreachable': True, 
            'msg': 'Failed to connect to the host via ssh: ssh: connect to host 172.66.110.122 port 22: Operation timed out\r\n'}}, 
        '172.66.110.15': {'status': 'ok', 'result': 
            {'changed': True, 
            'stderr': 'Shared connection to 172.66.110.15 closed.\r\n', 
            'stdout_lines': ['\x1b[32m+--------------------------------------------------------------+\x1b[0m', 
                        '\x1b[32m|             Welcome to Centos System init                    |\x1b[0m', 
                        '\x1b[32m+--------------------------------------------------------------+\x1b[0m', 
                        'vm172-66-110-15.ksc.com'], 'rc': 0, '_ansible_no_log': False, 
                        'stdout': '\x1b[32m+--------------------------------------------------------------+\x1b[0m\r\n\x1b[32m|             Welcome to Centos System init                    |\x1b[0m\r\n\x1b[32m+--------------------------------------------------------------+\x1b[0m\r\nvm172-66-110-15.ksc.com\r\n'}}}
        
        ------------------
        
        {"instanceId": {"PrivateIp": "172.66.110.12", "PublicIp":"202.202.202.202", init_result:{"status":"ok", "result":{}}}}
        
        
        
        '''


        for ip, results in init_result.items():
            for _instance_data in ecs_list:
                if 'PrivateIp' in _instance_data and _instance_data['PrivateIp'] == ip:
                    _instance_data['init_result'] = results
        print(ecs_list)
        return ecs_list
    except Exception as e:
        traceback.print_exc()
        return ecs_list


def main():
    pass


if __name__ == '__main__':
    main()
