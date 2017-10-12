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
from django.conf.urls import url, include
import operating.views as operating_views


urlpatterns = [
    url(r'^$', operating_views.index, name='index'),
    url(r'^filetransfer/$', operating_views.filetransfer, name='filetransfer'),
    url(r'^fileupload/$', operating_views.fileupload, name='fileupload'),
    url(r'^addjob/$', operating_views.add_job, name='addjob'),

    url(r'^job_result/(?P<job_id>\w+)/$', operating_views.job_result, name='job_result'),
    url(r'^job_process/(?P<job_id>\w+)/$', operating_views.job_process, name='job_process'),
    url(r'^list/$', operating_views.job_list, name='list'),
    url(r'^job_list_page/$', operating_views.job_list_page, name='job_list_page'),

    url(r'^cronjobs/$', operating_views.cronjobs, name='cronjobs'),
    url(r'^add_cronjobs/$', operating_views.add_cronjobs, name='add_cronjobs'),
    url(r'^page/$', operating_views.page, name='page'),
    url(r'^remove_cron_line/$', operating_views.remove_cron_line, name='remove_cron_line'),
    url(r'^start_cron/$', operating_views.start_cron, name='start_cron'),
    url(r'^stop_cron/$', operating_views.stop_cron, name='stop_cron'),
    url(r'^cronjobs/cron_update/(?P<crn_id>\w+)/$', operating_views.cron_update, name='cron_update'),

]
