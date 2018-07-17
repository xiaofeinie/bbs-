"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from blog import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('', views.index),
    path('logout/', views.logout),
    path('on_found', views.on_found),
    path('code/', views.code),


    path('backend/', views.backend),
    path('upload/', views.upload),
    path('addarticle/', views.add_article),
    path('deldarticle/', views.delarticle),
    re_path('uppdarticle/(?P<id>\d+)', views.upparticle),


    re_path('digg/', views.digg),
    re_path('pinglun/', views.pinglun),

    re_path('(?P<username>\w+)/p/(?P<article_id>\d+)', views.article_detail),
    re_path('(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<params>.*)', views.homesite),

    re_path('(?P<username>\w+)', views.homesite)
]
