#!/usr/bin/env python
# coding:utf-8
from kscore.session import get_session

# 密钥
ACCESS_KEY_ID = "__ACCESS_KEY_ID__"
SECRET_ACCESS_KEY = "__SECRET_ACCESS_KEY__"

s = get_session()

client = s.create_client("kec", "cn-beijing-6", use_ssl=False, ks_access_key_id=ACCESS_KEY_ID, ks_secret_access_key=SECRET_ACCESS_KEY)

data = client.describe_instances(InstanceId=['03ab30e6-c1b8-4a4d-867a-ced6110edd06','dc53a16a-7775-445a-bc80-25dcc513d403'])
print(data)
print("jjjjjjjjjjjjjjjjjjjjjjjjjjj")
print(len(data['InstancesSet']))
print(client.describe_images())
# for i in client.describe_images()['ImagesSet']:
#     if 'Centos-7' in i['Name']:
#         print(i)


client_vpc = s.create_client("vpc", "cn-beijing-6", use_ssl=False, ks_access_key_id=ACCESS_KEY_ID, ks_secret_access_key=SECRET_ACCESS_KEY)
print(dir(client_vpc))
print("-----------------------------------")
print(client_vpc.describe_vpcs())
for i in client_vpc.describe_vpcs()['VpcSet']:
    print(i)
print("-----------------------------------")
print(client_vpc.describe_subnets())
for i in client_vpc.describe_subnets()['SubnetSet']:
    if i['VpcId'] == '509ffb8a-b6b6-495a-8f60-29e3345b960b':
        print(i)

print("-----------------------------------")
print(client_vpc.describe_security_groups())
for i in client_vpc.describe_security_groups()['SecurityGroupSet']:
    if 'vpc_firewall' in str(i):
        print(i)

run_result = client.run_instances(#ImageId='cb7a02d2-a6e2-4bc4-a3a0-5ee8b131a451',
                     InstanceType='I1.1B',
                     DataDiskGb=30,
                     MaxCount=2,
                     MinCount=2,
                     InstancePassword='__password__',
                     SubnetId='60ba1af8-ed1e-437c-8235-feccfc0a771f',
                     #SecurityGroupId='1f66de4c-a5c2-4e94-a416-58ec0b5a5a21',
                     InstanceName='bj-ksy-vn-java-01',
                     ChargeType='Daily'
                     )
#
# for i in run_result['InstancesSet']:
#     print(i['InstanceId'])
print(run_result)
print(client.describe_instances(InstanceId=[x['InstanceId'] for x in run_result['InstancesSet']]))

# 套餐类型
'''
I1.4B	4	8	0-500
I1.4C	4	16	0-500
I1.8A	8	8	0-800
I1.8B	8	16	0-800
'''
