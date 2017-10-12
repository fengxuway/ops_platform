#!/usr/bin/python
# coding: utf-8
from django.shortcuts import render, redirect
from server.models import Server
from django.db.models import Count
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required


@login_required
def index(request):
    server_total_count= Server.objects.count()
    grid_total_count = 0
    service_total_count = 0
    image_total_count = 0
    image_list = []
    service_list = []
    grid_list = []
    # for m in Image.objects.values('service_name').annotate(count=Count('service_name')).order_by('-count'):
    #     m['percent'] = m['count'] * 0.1 / image_total_count
    #     image_list.append(m)
    # for m in Service.objects.values('service_name').annotate(count=Count('service_name')).order_by('-count'):
    #     m['percent'] = m['count'] * 0.1 / service_total_count
    #     service_list.append(m)
    # for m in Grid.objects.values('area').annotate(count=Count('area')).order_by('-count'):
    #     m['percent'] = m['count'] * 0.1 / grid_total_count
    #     grid_list.append(m)
    return render(request, 'index.html', locals())


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    print(request.POST)

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    if not username or not password:
        message = '用户名密码不能为空！'
        return render(request, 'login.html', locals())

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return redirect('index')
    else:
        message = '用户名或密码有误！'
        return render(request, 'login.html', locals())


def logout(request):
    auth.logout(request)
    return redirect('index')


def main():
    pass


if __name__ == "__main__":
    main()
