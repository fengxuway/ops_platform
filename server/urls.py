"""cms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# coding=utf-8
from django.conf.urls import url, include
import server.views as server_views
import server.views_domain as domain_views
import cmdb.views as cmdb_views

urlpatterns = [
    # url(r'^$', server_views.index, name='index'),
    url(r'^page/', server_views.page, name='page'),
    url(r'^page_enabled/', server_views.page_enabled, name='page_enabled'),
    url(r'^upload/', server_views.upload, name='upload'),
    url(r'^add/', server_views.add, name='add'),
    url(r'^update/(?P<srv_id>\d+)/', server_views.update, name='update'),
    # url(r'^remove/', server_views.remove_server, name='remove'),
    url(r'^search_by_area/', server_views.search_by_area, name='search_by_area'),
    url(r'^view_log/(?P<srv_id>\d+)/', server_views.view_log, name='view_log'),
    url(r'^connect/(?P<srv_id>\d+)/', server_views.connect, name='connect'),

    # domain urls
    url(r'^domain/$', domain_views.index, name='domain_index'),
    url(r'^domain/page/', domain_views.page, name='domain_page'),
    url(r'^domain/add/', domain_views.add, name='domain_add'),
    url(r'^domain/update/(?P<dmn_id>\d+)/', domain_views.update, name='domain_update'),
    url(r'^domain/remove/', domain_views.remove, name='domain_remove'),
    url(r'^domain/upload/', domain_views.upload, name='domain_upload'),

    # cmdb
    url(r'^$', cmdb_views.service_info, name='index'),
    url(r'^index_phone', cmdb_views.service_info_phone, name='index_phone'),
    url(r'^update_info/', cmdb_views.update_info, name='update_info'),
    url(r'^job_list_page/', cmdb_views.job_list_page, name='job_list_page'),
    url(r'^job_list_page_phone/', cmdb_views.job_list_page_phone, name='job_list_page_phone'),
    url(r'^eip_page/', cmdb_views.eip_page, name='eip_page'),
    url(r'^export/', cmdb_views.export, name='export'),
    url(r'^show_del_server/', cmdb_views.show_del_server, name='show_del_server'),
    url(r'^del_list_page/', cmdb_views.del_list_page, name='del_list_page'),
    url(r'^update_status_page/', cmdb_views.update_status_page, name='update_status_page'),
    url(r'^show_update_info/', cmdb_views.show_update_info, name='show_update_info'),
    url(r'^do_operate/', cmdb_views.do_operate, name='do_operate'),
    url(r'^add_server/', cmdb_views.add_server, name='add_server'),
    url(r'^check_ssh_copy/', cmdb_views.check_ssh_copy, name='check_ssh_copy'),
    url(r'^services/', cmdb_views.restart_service, name='restart_service'),

    url(r'^modify/(?P<srv_id>\d+)/', cmdb_views.modify, name='modify'),
    url(r'^deeply_delete/', cmdb_views.deeply_delete, name='deeply_delete'),

    url(r'^group/', cmdb_views.group_index, name='group'),
    url(r'^eip/', cmdb_views.eip_index, name='eip'),
    url(r'^group_page/', cmdb_views.group_page, name='group_page'),
    url(r'^add_group/', cmdb_views.add_group, name='add_group'),
    url(r'^get_servers/', cmdb_views.get_servers, name='get_servers'),
    url(r'^update_group/(?P<gid>\d+)/', cmdb_views.update_group, name='update_group'),
    url(r'^remove_group/', cmdb_views.remove_group, name='remove_group'),

    # api
    url(r'^add_server_api/', cmdb_views.add_server_api, name='add_server_api'),
    url(r'^route_shell/', cmdb_views.route_shell, name='route_shell'),

]
