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
@permission_classes([IsAdminUser])
def get_servers_info_api(request):
	asociacion_cruda = asociacionAS.Return_Server_Admin()
	user_admin_service = request.data['username']
	asociacion_datos = asociacionAS.return_server_admin_JSON(asociacion_cruda, user_admin_service)
	list_info_servers = []
	list_token_client = request.data['tokens_sessions']
	i=0
	lista_token = [list_token_client]
	if len(asociacion_datos.get('servers')) == 0:
		datos = json.loads(json.dumps(asociacion_datos.get('servers')))
		return Response(datos)
	for token in lista_token:
		ip_client = asociacion_datos.get('servers')[i]
		url_client_monitor = 'https://' + ip_client + '/monitor_server/'
		headers={'Authorization': 'Token %s' % token}
		respuesta = requests.get(url_client_monitor, headers=headers, verify=False)
		info_servidor = respuesta.json()
		info_servidor['servidor'] = ip_client
		list_info_servers.append(info_servidor)
		i = i+1
	datos = json.loads(json.dumps(list_info_servers))
	return Response(datos)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def session_ephemeral_admin(request):
	if request.method == 'POST':

		usuario = request.data['username']
		asociacion_cruda = asociacionAS.Return_Server_Admin()
		asociacion_datos = asociacionAS.return_server_admin_JSON(asociacion_cruda, usuario)
		token_sesion_servidores = []
		for ip_cliente in asociacion_datos.get('servers'):
			url_client_autenticacion = 'https://' + ip_cliente + '/autenticacion_clienteAPI/'
			url_client_user_ephemeral = 'https://' + ip_cliente + '/asociar_API_cliente/'
			token_master_usr = asociacionAS.return_token(url_client_autenticacion, VE.USR_CLIENT_SERVICE, VE.PASS_CLIENT_SERVICE)
			usuario, passwd = asociacionAS.record_user_ephemeral(url_client_user_ephemeral, token_master_usr)
			token_cliente_servidor = asociacionAS.return_token(url_client_autenticacion, usuario, passwd)
			token_sesion_servidores.append(token_cliente_servidor)
		return_tokens = {'token_sessions': token_sesion_servidores}
		tokens_session_server = json.loads(json.dumps(return_tokens))
		return Response(tokens_session_server)


	elif request.method == 'DELETE':

		usuario = request.data['username']
		asociacion_cruda = asociacionAS.Return_Server_Admin()
		asociacion_datos = asociacionAS.return_server_admin_JSON(asociacion_cruda, str(usuario))
		list_token_client = request.data['tokens_sessions']
		lista_token = [list_token_client]
		logging.info(list_token_client)	###		###		###
		logging.info(lista_token)	###		###		###
		i = 0
		for token in lista_token:
			ip_client = asociacion_datos.get('servers')[i]
			url_client_autenticacion = 'https://' + ip_client + '/autenticacion_clienteAPI/'
			url_client_userE = 'https://' + ip_client + '/asociar_API_cliente/'
			token_master_usr = asociacionAS.return_token(url_client_autenticacion, VE.USR_CLIENT_SERVICE, VE.PASS_CLIENT_SERVICE)
			if not asociacionAS.delete_user_ephemeral(url_client_userE, token_master_usr, token):
				logging.info('Usuario efimero del servidor '+str(ip_client)+' no se puedo eliminar')
			i=i+1
		return HttpResponse(status=204)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def listar_asociaciones(request):
	asociacion_cruda = asociacionAS.Return_Server_Admin()
	asociacion_datos = asociacionAS.return_server_admin_all(asociacion_cruda)
	return Response(asociacion_datos)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def api_asociar_servidores(request):
	if request.method == 'POST':
		try:
			user_admin_service = request.data['username']
			ip_server = request.data['server_ip']
		except:
			logging.error('Formato invalido')
			return HttpResponse(status=400)

		vacio = ''
		if not user_admin_service != vacio or not ip_server != vacio:    
			logging.error('Se deben completar campos username y server_ip')
			return HttpResponse(status=400)
		if back_end.recuperar_admin(user_admin_service):
			back_end.registro_servidor(user_admin_service, ip_server)
		else:
			if back_end.registro_admin(user_admin_service):
				back_end.registro_servidor(user_admin_service, ip_server)
			else:
				logging.error('Asociacion corrupta de administrador a servidor')
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
def api_administradores(request):
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
		asociacion_cruda = asociacionAS.Return_Server_Admin()
		asociacion_datos = asociacionAS.return_server_admin_JSON(asociacion_cruda, user)
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
