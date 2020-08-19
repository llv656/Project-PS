from django.db import models

class IPs(models.Model):
	ip = models.GenericIPAddressField(null=False, blank=False, unique=True)
	ultima_peticion = models.DateTimeField(null=False, blank=False)
	intentos = models.IntegerField(null=False, blank=False, default=0)
	intentos_multifactor = models.IntegerField(null=False, blank=False, default=0)
	total_intentos = models.IntegerField(null=False, blank=False, default=0)

class Sesiones(models.Model):
	id_sesion = models.CharField(max_length=30, null=False, blank=False, unique=True)
	usuario = models.CharField(max_length=30, null=False, blank=False)
	login = models.DateTimeField(null=False, blank=False)
	logout = models.DateTimeField(blank=False)
	ip = models.GenericIPAddressField(null=False, blank=False)

class ListaNegra(models.Model):
	ip = models.GenericIPAddressField(null=False, blank=False, unique=True)
