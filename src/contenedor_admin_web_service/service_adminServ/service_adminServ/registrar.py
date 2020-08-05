from asociacionAPI import models
from django.contrib.auth.models import User

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
		registro = models.Admin.objects.get(user_admin=admin)
		return True
	except:
		return False
