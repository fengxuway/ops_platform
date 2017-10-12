"""ntdeploy URL Configuration

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
from django.contrib import admin
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^server/', include('server.urls', namespace='server')),
    url(r'^options/', include('options.urls', namespace='options')),
    url(r'^grid/', include('grid.urls', namespace='grid')),
    url(r'^operating/', include('operating.urls', namespace='operating')),
    url(r'^dashboard/', include('dashboard.urls', namespace='dashboard')),
    url(r'^api/', include('api.urls', namespace='api')),

    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^accounts/login/$', views.login),
    url(r'^accounts/logout/$', views.logout),

    # url(r'^accounts/login/$', login, name='login'),
    # url(r'^accounts/logout/$', logout, name='logout'),
]
