from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from rest_framework.decorators import parser_classes
import json
from servicios_adminServ import settings

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def servidores_monitor(request):
	if request.method == 'GET': 
		datos_raw = '[{"memoria": "100.254%", "disco": "77.56%", "process": "86.26%"}]' 
		datos = json.loads(datos_raw) 
		
		return Response(datos) 

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def asociar_recordAPI(request):
	operacion = request.data['operacion']
	serverIP = request.data['username']
	password_serv = request.data['password']
	if operacion == 'create':
		user = User.objects.create_user(serverIP, 'null', password_serv)
		user.save()
	return Response(request.data)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def admin_recordAPI(request):
	operacion = request.data['operacion']
	user_admin = request.data['username']
        password_admin = request.data['password']
        if operacion == 'create':
                user = User.objects.create_user(user_admin, 'null', password_admin)
                user.save()
        return Response(request.data)
