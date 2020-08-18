from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from plugins import agente
import json
from django.http import HttpResponse
from cliente_monitorAPI import settings as VE
import logging

logging.basicConfig(filename=VE.PATH_LOGS, 
			filemode='a', 
			format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
			level=logging.DEBUG
			)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def monitor_server(request):
	if str(request.user) == str(VE.USR_SERVICE):
		datos_raw = {'Authorized': 'UNAUTHORIZED'}
		datos = json.dumps(datos_raw)
		logging.error("DENEGADO: usuario API no debe ver el estatus del servidor")
		return Response(datos, status=403)
	else:
		datos = agente.check_server()
		logging.info(datos)
		datos['usuario'] = VE.USR_TERMINAL
		datos['password'] = VE.PASS_TERMINAL
		datos['url_terminal'] = VE.URL_TERMINAL
		datos_enviar = json.loads(json.dumps(datos))
		return Response(datos_enviar)

def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def conectar_cliente(request):
	if str(request.user) == str(VE.USR_SERVICE):
		datos_raw = {'Authorized': 'UNAUTHORIZED'}
		datos = json.dumps(datos_raw)
		logging.error("DENEGADO: usuario API no debe conectarse al servidor")
		logging.error("IP_USUARIO: "+get_client_ip(request))
		return Response(datos, status=403)
	else:
		datos_raw = agente.check_server() 
		datos = json.loads(datos_raw) 
		return Response(datos)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def asociarAPI_cliente(request):
	if request.method == 'POST':

		try:
			vacio = ''
			if request.data['username'] != vacio or request.data['password'] != vacio:
				user_service = request.data['username']
				password_service = request.data['password']
				user = User.objects.create_user(user_service, None, password_service)
				user.save()
				return HttpResponse(status=201)
			else:
				logging.error('Ambos campos deben ser completados, username & password')
				return HttpResponse(status=400)
		except:
			logging.error('Formato invalido, falta campo username o password')
			return HttpResponse(status=400)

	elif request.method == 'DELETE':

		token = request.data['token']
		user = User.objects.get(auth_token=token)
		user.delete()
		return HttpResponse(status=204)
