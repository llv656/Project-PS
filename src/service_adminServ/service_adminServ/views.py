from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
import json
from service_adminServ import settings as VE
from service_adminServ import registrar as back_end
from asociacionAPI.serializers import AdminSerializer
import requests


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def servers_admin(request):
	if request.method == 'GET': 
		#Se debe de buscar la forma para almacenar el servidor y el administrador como llave foranea

		respuesta = requests.get('http://192.168.100.176:8080/monitor_server/', headers=headers1)
		datos_raw = '[{"memoria": "100.254%", "disco": "77.56%", "process": "86.26%"}]' 
		datos = json.loads(datos_raw) 
		
		return Response(datos) 

@api_view(['POST', 'DELETE'])
@authentication_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def asociar_API(request):
	try:
		if request.data['username'] != ' ' or request.data['server_ip'] != ' ':
			user_admin_service = request.data['username']
			ip_server = request.data['ip_server']  # En esta parte se debe de registrar al servidor, y el administrador se debe asociar como llave foranea 
			if back_end.recuperar_admin(user_admin_service):
				back_end.registro_servidor(ip_server, user_admin_service)
				#registrar solo servidor
			else:
				if not back_end.registro_admin(user_admin_service):
					print('ALERTA: Asociacion corrupta de administrador a servidor')
					return HttpResponse(status=400)
				back_end.registro_admin(user_admin_service)
				back_end.registro_servidor(ip_server, user_admin_service)
		else:
			print('Se deben completar ambos campos')  #logging.error('Se deben completar ambos campos')
			return HttpResponse(status=400)
	except:
		print('Formato invalido')
		return HttpResponse(status=400)


	if request.method == 'DELETE':
		user = User.objects.get(username=user_admin)
	return Response(request.data)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def admin_recordAPI(request):
	try:
		if request.data['username'] != '':
			user_service = request.data['username']
		else:
			print('El campo no puede estar vacio, username')  #logging.error('El campo no puede estar vacio, username')
			return HttpResponse(status=400)
	except:
		print ('Formato invalido, falta campo username')  #logging.error('Formato invalido, falta campo username')
		return HttpResponse(status=400)

	if request.method == 'POST':
		try:
			if request.data['password'] != '':
				password_service = request.data['password']
				user = User.objects.create_user(user_service, None, password_service)
				user.save()
				return HttpResponse(status=201)
			else:
				print('El campo no puede estar vacio, password') # logging.error('El campo no puede estar vacio, password')
				return HttpResponse(status=400)
		except Exception:
			print('Formato invalido, falta campo password')  #logging.error('Formato invalido, falta campo password')
			return HttpResponse(status=400)

	elif request.method == 'DELETE':
		user = User.objects.get(username=user_service)
		user.delete()
		return HttpResponse(status=204)
