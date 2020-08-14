from django.db.models import Prefetch
from asociacionAPI.serializers import AdminSerializer
from asociacionAPI.models import Admin
from service_adminServ import settings as VE
from urllib.request import urlopen
import json
import base64, os
import urllib3, requests
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

class return_server_admin():
	queryset = Admin.objects.all()
	serializer_admin = AdminSerializer
	def get_queryset(self):
		queryset = super().get_queryset()
		queryset = queryset.prefetch_related(Prefetch('servers'))
		return queryset

def return_server_adminJSON(instancia_admin_server, admin):
	admin_serializer = instancia_admin_server.serializer_admin(Admin.objects.get(user_admin=admin)) #Admin.objects.get(user_admin='admin2')) #Pasar el nombre del administrador
	admin_servers =	json.dumps(admin_serializer.data)
	return json.loads(admin_servers)

def return_server_admin_all(instancia_admin):
	i = 0
	admin = Admin.objects.all()
	admin_server = []
	for i in range(admin.count()):
		admin_serializer = instancia_admin.serializer_admin(admin[i])
		admin_servers = admin_serializer.data
		admin_server.append(admin_servers)
	return json.loads(json.dumps(admin_server))

def record_userE(url_record, token_master):
	headers={'Authorization': 'Token %s' % token_master}
	user = base64.b64encode(os.urandom(16)).decode('utf-8')
	passwd = base64.b64encode(os.urandom(16)).decode('utf-8')
	data={'username': user, 'password': passwd}
	try:
		solicitud = requests.post(url_record, headers=headers, data=data, verify=False)
		return user, passwd
	except BaseException:
		logging.exception('Error durante el registro del usuario efimero en el cliente')
		return False

def delete_userE(url_record, token_master, token_userE):
	headers={'Authorization': 'Token %s' % token_master}
	data={'token': token_userE}
	try:
		solicitud = requests.delete(url_record, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error el eliminar el usuario efimero en el cliente')
		return False

def return_token(url_autenticacion, username, passwd):
	data={'username': username,'password': passwd}
	try:
		token_service = requests.post(url_autenticacion, data=data, verify=False)
		return token_service.json()['token']
	except BaseException:
		logging.exception('No se pudo obtener token del API cliente')
		return False
