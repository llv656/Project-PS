from django.db.models import Prefetch
from asociacionAPI.serializers import AdminSerializer
from asociacionAPI.models import Admin
import json
import base64
import os
import requests

class return_server_admin():
	queryset = Admin.objects.all()
	serializer_admin = AdminSerializer
	def get_queryset(self):
		queryset = super().get_queryset()
		queryset = queryset.prefetch_related(Prefetch('servers'))
		return queryset

def return_server_adminJSON(instancia_admin, admin):
	admin_serializer = instancia_admin.serializer_admin(Admin.objects.get(user_admin=admin)) #Admin.objects.get(user_admin='admin2')) #Pasar el nombre del administrador
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
		solicitud = requests.post(url_record, headers=headers, data=data)
		return user, passwd
	except:
                return False

def delete_userE(url_record, token_master, userE):
	headers={'Authorization': 'Token %s' % token_master}
	data={'username': userE}
	try:
		solicitud = requests.delete(url_record, headers=headers, data=data)
		return True
	except:
		return False

def return_token(url_autenticacion, username, passwd):
	data={'username': username,'password': passwd}
	try:
		token_service = requests.post(url_autenticacion, data=data)
		return token_service.json()['token']
	except:
		return False
