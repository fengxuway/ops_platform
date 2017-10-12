#!/usr/bin/env python
# coding:utf-8

from kscore.session import get_session

# 密钥
ACCESS_KEY_ID = "__ACCESS_KEY_ID__"
SECRET_ACCESS_KEY = "__SECRET_ACCESS_KEY__"

s = get_session()

client = s.create_client("eip", "cn-beijing-6", use_ssl=False, ks_access_key_id=ACCESS_KEY_ID, ks_secret_access_key=SECRET_ACCESS_KEY)

print(client.describe_addresses())
print(client.get_lines())
print('---')

# print(client.allocate_address(ChargeType="Daily", BandWidth=50, LineId='5fc2595f-1bfd-481b-bf64-2d08f116d800'))

# 创建EIP结果
#{'AllocationId': '478a2f0b-5dfb-404d-bba8-0120787e93ee', 'PublicIp': '120.92.93.112', 'RequestId': '7b750f99-08d9-47e8-97f4-87de4d9ffd64'}
#{'PublicIp': '120.92.18.69', 'RequestId': '49363671-fa53-4c98-a286-eb3c5605f710', 'AllocationId': '0395cf2e-f26d-46c4-826d-c23002b59158'}
# 绑定EIP到实例：
print(client.associate_address(AllocationId='0395cf2e-f26d-46c4-826d-c23002b59158', InstanceType='Ipfwd', InstanceId='f748e3ba-457b-4a3d-99ae-0a441f7b918b', NetworkInterfaceId='93e75e89-6bb8-4c44-8e9e-f0e0e8bccf93'))
# {'RequestId': 'bfc3c418-222d-4e0a-b16e-e276545a350a', 'Return': True}
