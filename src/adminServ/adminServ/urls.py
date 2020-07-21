"""adminServ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from adminServ.views import *
from adminServ import settings

urlpatterns = [
   path('login/', login),
   path('', login),
   path('bienvenida_admin/', bienvenida_admin, name='bienvenida_admin'),
   path('multifactor/', multifactor, name='multifactor'),
   path('%sregistro_administradores/' % settings.PATH_PREFIX, registro_administradores, name='registro_administradores'),
   path('%sregistro_servidores/' % settings.PATH_PREFIX, registro_servidores, name='registro_servidores'),
   path('%sasociarAS/' % settings.PATH_PREFIX, asociarAS, name='asociarAS'),
   path('%slogout/' % settings.PATH_PREFIX, logout, name='logout'),
   path('multifactorA/', multifactorA, name='multifactorA'),
   path('bienvenida_adminA/', bienvenida_adminA, name='bienvenida_adminA'),
   path('%sstatus_server/' % settings.PATH_PREFIX, status_server, name='status_server'),
   path('%sserver_connect/' % settings.PATH_PREFIX, server_connect, name='server_connect'),
   path('%slogoutA/' % settings.PATH_PREFIX, logoutA, name='logoutA'),
]
