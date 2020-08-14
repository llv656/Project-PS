from registroA import models
from adminServ import operaciones_ws
from adminServ import settings as VE
from adminServ.modificar import modificar_campos
import os, base64
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def existencia_administrador(admin):
	try:
		registro = models.Administradores.objects.get(user_admin=admin)
		return True
	except:
		return False

def modificar_administrador(admin, lista, lista_campos):
	try:
		registro = models.Administradores.objects.get(user_admin=admin)
		actualizacion = modificar_campos.actualizar_campos_admin(registro, admin, lista, lista_campos)
		return actualizacion
	except BaseException:
		logging.exception('Error de actualizacion, Administrador')
		contexto="Administrador no existe"
		return contexto, False

def eliminar_administrador(admin):
	try:
		registro = models.Administradores.objects.get(user_admin=admin)
		if operaciones_ws.eliminar_admin(admin):
			registro.delete()
			return '', True
		else:
			contexto = "Ocurrio un error mientras se intentaba eliminar al administrador, intente mas tarde"
			return contexto, False
	except BaseException:
		logging.exception('Error al eliminar administrador')
		contexto="Administrador no existe"
		return contexto, False
