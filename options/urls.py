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
import options.views


urlpatterns = [
    url(r'^$', options.views.index, name='index'),
    url(r'^add_data', options.views.add_data, name='add_data'),
    url(r'^remove_data', options.views.remove_data, name='remove_data'),
    url(r'^page/', options.views.page, name='page'),
    url(r'^data_option/', options.views.data_option, name='data_option'),

]
