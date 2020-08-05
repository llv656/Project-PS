from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from service_adminServ import settings as VE
from service_adminServ import registrar as back_end
from asociacionAPI import asociacionAS
from django.http import HttpResponse
import requests
import json

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def info_serversAPI(request):
	asociacion = asociacionAS.return_server_admin()
	user_admin_service = request.data['username']
	asociacion_datos = asociacionAS.return_server_adminJSON(asociacion, user_admin_service)
	part_url_client = VE.URL_CLIENT_SERVICE.split(',')
	list_info_servers = []
	list_token_client = request.data['tokens_sessions']
#	for i in range(0, len(list_token_client)):
	ip_client = asociacion_datos.get('servers')[0]
	url_client_monitor = part_url_client[0] + ip_client + part_url_client[1] + '/monitor_server/'
	headers={'Authorization': 'Token %s' % list_token_client}  #[0]}  #remplazar algunos 0 con i
	respuesta = requests.get(url_client_monitor, headers=headers)
	list_info_servers.append(respuesta.json())

	datos = json.loads(json.dumps(list_info_servers))
	return Response(datos) 

@api_view(['GET', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def admin_sesionE(request):
	asociacion = asociacionAS.return_server_admin()
	asociacion_datos = asociacionAS.return_server_adminJSON(asociacion, str(request.user))
	part_url_client = VE.URL_CLIENT_SERVICE.split(',')
	if request.method == 'GET':
		token_sesion_servidores = []
#		for i in range(len(asociacion_datos.get('servers'))):
		ip_client = asociacion_datos.get('servers')

		url_client_autenticacion = part_url_client[0] + ip_client[0] + part_url_client[1] + '/autenticacion_clienteAPI/'
		url_client_userE = part_url_client[0] + ip_client[0] + part_url_client[1] + '/asociarAPI_cliente/'
		print(ip_client)
		token_master_usr = asociacionAS.return_token(url_client_autenticacion, VE.USR_CLIENT_SERVICE, VE.PASS_CLIENT_SERVICE)
		usuario, passwd = asociacionAS.record_userE(url_client_userE, token_master_usr)

		token_cliente_servidor = asociacionAS.return_token(url_client_autenticacion, usuario, passwd)
#			token_sesion_servidores.append(token_cliente_servidor)
	
		return_tokens = {'token_sessions': token_cliente_servidor}
		tokens_session_server = json.loads(json.dumps(return_tokens))
		return Response(tokens_session_server)
	elif request.method == 'DELETE':
		for i in range(len(asociacion_datos.get('servers'))):
			ip_client = asociacion_datos.get('servers')[i]
			url_client_autenticacion = part_url_client[0] + ip_client + part_url_client[1] + '/autenticacion_clienteAPI/'
			url_client_userE = part_url_client[0] + ip_client + part_url_client[1] + '/asociarAPI_cliente/'
			token_master_usr = asociacionAS.return_token(url_client_autenticacion, VE.USR_CLIENT_SERVICE, VE.PASS_CLIENT_SERVICE)

			#sacar token de los datos del request, para eliminar su usurio efimero asociado

			if not asociacionAS.delete_userE(url_client_userE, token_master_usr, userE):
				print('Usuario efimero del servidor '+str(ip_client)+' no se puedo eliminar')
				#return HttpResponse(status=204)
		return HttpResponse(status=204)
#	return HttpResponse(json.dumps(asociacion_datos), content_type='application/json')

@api_view(['GET'])
#@authentication_classes([TokenAuthentication])
#@throttle_classes([UserRateThrottle])
#@permission_classes([IsAdminUser])
def listar_AS(request):
        asociacion = asociacionAS.return_server_admin()
        asociacion_datos = asociacionAS.return_server_admin_all(asociacion)
        return Response(asociacion_datos)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def asociar_API(request):
	if request.method == 'POST':
		try:
			user_admin_service = request.data['username']
			ip_server = request.data['server_ip']
			if user_admin_service != ' ' and ip_server != ' ':
				if back_end.recuperar_admin(user_admin_service):
					back_end.registro_servidor(user_admin_service, ip_server)
				else:
					if back_end.registro_admin(user_admin_service):
						back_end.registro_servidor(user_admin_service, ip_server)
					else:
						print('ALERTA: Asociacion corrupta de administrador a servidor')
						return HttpResponse(status=400)
			else:
				print('Se deben completar ambos campos')
				return HttpResponse(status=400)
		except:
			print('ALERTA: Formato invalido')
			return HttpResponse(status=400)
	elif request.method == 'DELETE':
		user_admin_service = request.data['username']
		user = User.objects.get(username=user_admin)
		user.delete()
		return HttpResponse(status=204)
	return HttpResponse(status=201)

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
