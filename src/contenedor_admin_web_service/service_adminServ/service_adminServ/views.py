from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User
from service_adminServ import settings as VE
from service_adminServ import registrar as back_end
from urllib.request import urlopen
from asociacionAPI import asociacionAS
from django.http import HttpResponse
import requests, urllib3
import json
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

urllib3.disable_warnings()

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
	i=0
	lista_token = [list_token_client]
	if len(asociacion_datos.get('servers')) == 0:
		datos = json.loads(json.dumps(asociacion_datos.get('servers')))
		return Response(datos)
	for token in lista_token:
		ip_client = asociacion_datos.get('servers')[i]
		url_client_monitor = part_url_client[0] + ip_client + part_url_client[1] + '/monitor_server/'
		headers={'Authorization': 'Token %s' % token} #list_token_client}  #[0]}  #remplazar algunos 0 con i
		respuesta = requests.get(url_client_monitor, headers=headers, verify=False)
		info_servidor = respuesta.json()
		info_servidor['servidor'] = ip_client
		list_info_servers.append(info_servidor)
		i = i+1
	
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

		for ip_cliente in asociacion_datos.get('servers'):
			url_client_autenticacion = part_url_client[0] + ip_cliente + '/autenticacion_clienteAPI/'
			url_client_userE = part_url_client[0] + ip_cliente + '/asociarAPI_cliente/'
			token_master_usr = asociacionAS.return_token(url_client_autenticacion, VE.USR_CLIENT_SERVICE, VE.PASS_CLIENT_SERVICE)
			usuario, passwd = asociacionAS.record_userE(url_client_userE, token_master_usr)
			token_cliente_servidor = asociacionAS.return_token(url_client_autenticacion, usuario, passwd)
			token_sesion_servidores.append(token_cliente_servidor)
		return_tokens = {'token_sessions': token_sesion_servidores}
		tokens_session_server = json.loads(json.dumps(return_tokens))
		return Response(tokens_session_server)
	elif request.method == 'DELETE':
		
		for ip_client in asociacion_datos.get('servers'):
			url_client_autenticacion = part_url_client[0] + ip_client + part_url_client[1] + '/autenticacion_clienteAPI/'
			url_client_userE = part_url_client[0] + ip_client + part_url_client[1] + '/asociarAPI_cliente/'
			token_master_usr = asociacionAS.return_token(url_client_autenticacion, VE.USR_CLIENT_SERVICE, VE.PASS_CLIENT_SERVICE)
			#sacar token de los datos del request, para eliminar su usurio efimero asociado
			if not asociacionAS.delete_userE(url_client_userE, token_master_usr, token_userE):
				logging.info('Usuario efimero del servidor '+str(ip_client)+' no se puedo eliminar')
		return HttpResponse(status=204)
#	return HttpResponse(json.dumps(asociacion_datos), content_type='application/json')

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
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
						logging.error('Asociacion corrupta de administrador a servidor')
						return HttpResponse(status=400)
			else:
				logging.error('Se deben completar campos username y server_ip')
				return HttpResponse(status=400)
		except:
			logging.error('Formato invalido')
			return HttpResponse(status=400)

		return HttpResponse(status=201)
	if request.method == 'DELETE':
		servidor = request.data['server_ip']
		if back_end.eliminar_servidor(servidor):
			return HttpResponse(status=204)

@api_view(['POST', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def admin_recordAPI(request):
	try:
		if request.data['username'] != '':
			user_service = request.data['username']
		else:
			logging.error('El campo no puede estar vacio, username')
			return HttpResponse(status=400)
	except:
		logging.error('Formato invalido, falta campo username')
		return HttpResponse(status=400)

	if request.method == 'DELETE':
		try:
			user = User.objects.get(username=user_service)
		except:
			logging.error('No se encontro usuario')
			return HttpResponse(status=400)

		if not back_end.recuperar_admin(user_service):
			user.delete()
			return HttpResponse(status=204)
		asociacion = asociacionAS.return_server_admin()
		asociacion_datos = asociacionAS.return_server_adminJSON(asociacion, user)
		if back_end.eliminar_admin_servidores(user_service, asociacion_datos):
			user.delete()
			return HttpResponse(status=204)
		return HttpResponse(status=400)

	try:
		if request.data['password'] != '':
			password_service = request.data['password']
		else:
			logging.error('El campo no puede estar vacio, password')
			return HttpResponse(status=400)
	except BaseException:
		logging.exception('Formato invalido, falta campo password')
		return HttpResponse(status=400)

	if request.method == 'POST':
		user = User.objects.create_user(user_service, None, password_service)
		user.save()
		return HttpResponse(status=201)
	elif request.method == 'PUT':
		user = User.objects.get(username=user_service)
		user.password = password_service
		user.save()
		return HttpResponse(status=200)
