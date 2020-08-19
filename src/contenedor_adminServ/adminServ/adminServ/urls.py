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
   path('%sasociar_administrador_servidor/' % settings.PATH_PREFIX, asociar_administrador_servidor, name='asociar_administrador_servidor'),
   path('%slogout/' % settings.PATH_PREFIX, logout, name='logout'),
   path('multifactor_administrador/', multifactor_administrador, name='multifactor_administrador'),
   path('bienvenida_administrador_servidores/', bienvenida_administrador_servidores, name='bienvenida_administrador_servidores'),
   path('%sinformacion_servidor/' % settings.PATH_PREFIX, informacion_servidor, name='informacion_servidor'), 
   path('%slogout_admin_server/' % settings.PATH_PREFIX, logout_admin_server, name='logout_admin_server'),
]
