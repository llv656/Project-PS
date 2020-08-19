from registroA import models
from adminServ import operaciones_ws
from adminServ import settings as VE
from adminServ.modificar import modificar_campos
import os, base64
import re
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

CARACTERES_ESPECIALES = '_ -*+/.,$#%&()=\'\":;!|¬?¿~}{[]'
CARACTERES_ESPECIALES_NUMEROS = '_-*+/.,$#%&():;=\'\"!|¬?¿~}{[]0123456789'
MIN_LONG_NOMBRE = 2
MIN_LONG_APELLIDOS = 3
MIN_LONG_USER = 5
MAX_LONG_NOMBRE = 30
MAX_LONG_APELLIDOS = 60
MAX_LONG_USER = 30

def existencia_administrador(admin):
	try:
		models.Administradores.objects.get(user_admin=admin)
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

def verificar_campo(texto, caracteres, longitud_min, longitud_max):
	if len(texto) < longitud_min:
		return False
	if len(texto) > longitud_max:
		return False
	for letra in texto:
		for caracter in caracteres:
			if letra == caracter:
				return False
	return True

def verificar_token_telegram(token):
	pattern_token = "(^[0-9]+[:].[a-zA-Zr\(_\)r\(-\)])"
	coincide = re.search(pattern_token, token)
	if not coincide:
		return False
	if len(token) > 70:
		return False
	return True

def verificar_chat_id_telegram(chat_id):
	try:
		int(chat_id)
		if len(chat_id) > 15:
			return False
		return True
	except:
		return False

def verificar_campos_registro(user, nombre, apellidos, telegram_token, telegram_chat_id):
	if not verificar_campo(user, CARACTERES_ESPECIALES, MIN_LONG_USER, MAX_LONG_USER):
		contexto='Ingrese un nombre de usuario valido'
		return contexto, False
	if not verificar_campo(nombre, CARACTERES_ESPECIALES_NUMEROS, MIN_LONG_NOMBRE, MAX_LONG_NOMBRE):
		contexto='Ingrese un nombre valido' 
		return contexto, False
	if not verificar_campo(apellidos, CARACTERES_ESPECIALES_NUMEROS, MIN_LONG_APELLIDOS, MAX_LONG_APELLIDOS):
		contexto='Ingrese apellidos validos' 
		return contexto, False
	if not verificar_token_telegram(telegram_token):
		contexto='Formato de token invalido' 
		return contexto, False
	if not verificar_chat_id_telegram(telegram_chat_id):
		contexto='Formato de chat ID invalido'   
		return contexto, False
	return '', True
