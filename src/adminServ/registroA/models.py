from django.db import models

class Administradores(models.Model):
	user_admin = models.CharField(max_length=30, null=False, blank=False, unique=True)
	nombre = models.CharField(max_length=30, null=False, blank=False)
	apellidos = models.CharField(max_length=70, null=False, blank=False)
	telegram_token = models.CharField(max_length=60, null=False, blank=False)
	telegram_chatID = models.CharField(max_length=40, null=False, blank=False)
	passhash_admin = models.CharField(max_length=150, null=False, blank=False)
	passcif_webservice = models.CharField(max_length=150, null=False, blank=False)

class Servidores(models.Model):
	user_servidor = models.CharField(max_length=30, null=False, blank=False)
	ip = models.GenericIPAddressField(null=False, blank=False, unique=True)
	passcif_servidor = models.CharField(max_length=150, null=False, blank=False)
