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

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

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
		datos_raw = agente.check_server() 
		datos = json.loads(datos_raw) 
		return Response(datos)

@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAdminUser])
def asociarAPI_cliente(request):
	try:
		if request.data['username'] != '':
			user_service = request.data['username']
		else:
			logging.error('El campo no puede estar vacio, username')
			return HttpResponse(status=400)
	except:
		logging.error('Formato invalido, falta campo username')
		return HttpResponse(status=400)

	if request.method == 'POST':
		try:
			if request.data['password'] != '':
				password_service = request.data['password']
				user = User.objects.create_user(user_service, None, password_service)
				user.save()
				return HttpResponse(status=201)
			else:
				logging.error('El campo no puede estar vacio, password')
				return HttpResponse(status=400)
		except Exception:
			logging.error('Formato invalido, falta campo password')
			return HttpResponse(status=400)

	elif request.method == 'DELETE':
		user = User.objects.get(username=user_service)
		user.delete()
		return HttpResponse(status=204)
