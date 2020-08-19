from asociacionAPI import models
from django.contrib.auth.models import User
from service_adminServ import settings as VE
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def registro_admin(admin):
	if User.objects.get(username=admin):
		registro_admin = models.Admin(user_admin=admin)
		registro_admin.save()
		return True
	else:
		return False

def registro_servidor(admin, ip_server):
	try:
		registro_admin = models.Admin.objects.get(user_admin=admin)
		registro_server = models.Servers(admin=registro_admin, ip_server=ip_server)
		registro_server.save()
		return True
	except:
		return False

def recuperar_admin(admin):
	try:
		models.Admin.objects.get(user_admin=admin)
		return True
	except:
		return False

def eliminar_servidor(servidor):
	try:
		registro = models.Servers.objects.get(ip_server=servidor)
		registro.delete()
	except:
		logging.info('No se encontro el servidor, por lo tanto no se elimino')
	finally:
		return True

def eliminar_admin_servidores(admin, administrador_servidores):
	servers_asociados = list(administrador_servidores.values())
	if len(servers_asociados[1]) == 0:
		try:
			registro = models.Admin.objects.get(user_admin=admin)
			registro.delete()
			return True
		except:
			return False

	elif len(servers_asociados[1]) == 1:
		try:
			registro = models.Admin.objects.get(user_admin=admin)
			try:
				server = models.Servers.objects.get(ip_server=servers_asociados[1][0])
				server.delete()
				registro.delete()
				return True
			except BaseException:
				logging.exception('Error al eliminar servidor: '+servers_asociados[1][0])
				return False
		except BaseException:
			logging.exception('Error, eliminar administrador')
			return False

	elif len(servers_asociados[1]) > 1:
		try:
			registro = models.Admin.objects.get(user_admin=admin)
			try:
				for i in range(len(servers_asociados[1])):
					server = models.Servers.objects.get(ip_server=servers_asociados[1][i])
					server.delete()
				registro.delete()
				return True
			except BaseException:
				logging.exception('Error al eliminar servidor')
				return False
		except BaseException:
			logging.exception('Error al eliminar administrador')
			return False
