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
import api.views as views


urlpatterns = [
    # url(r'^$', service_views.index, name='index'),
    url(r'^ip_hostname/(?P<ip>[\d\.]+)$', views.ip_to_hostname, name='ip_hostname'),
    url(r'^kpi_ding/$', views.kpi_ding, name='kpi_ding'),

]
