from adminServ import inicio_sesion as back_end
from adminServ import registro as registros
from adminServ import operaciones_ws
from adminServ import settings as VE
from adminServ import servicio_admin
import os, base64

def actualizar_administrador(registro, admin, campo, valor):
	lista_negra_caracteres = servicio_admin.CARACTERES_ESPECIALES_NUMEROS
	if campo == 'nombre':
		longitud_min = servicio_admin.MIN_LONG_NOMBRE
		longitud_max = servicio_admin.MAX_LONG_NOMBRE
		if not servicio_admin.verificar_campo(list(valor.values())[0], lista_negra_caracteres, longitud_min, longitud_max):
			contexto = "Ingrese un nombre valido"
			return contexto, False
		registro.nombre=list(valor.values())[0]
	elif campo == 'apellidos':
		longitud_min = servicio_admin.MIN_LONG_APELLIDOS
		longitud_max = servicio_admin.MAX_LONG_APELLIDOS
		if not servicio_admin.verificar_campo(list(valor.values())[0], lista_negra_caracteres, longitud_min, longitud_max):
			contexto = "Ingrese apellidos validos"
			return contexto, False
		registro.apellidos=list(valor.values())[0]
	elif campo == 'telegram_t':
		if not servicio_admin.verificar_token_telegram(list(valor.values())[0]):
			contexto = "Formato de TOKEN invalido"
			return contexto, False
		registro.telegram_token=list(valor.values())[0]
	elif campo == 'telegram_i':
		if not servicio_admin.verificar_chat_id_telegram(list(valor.values())[0]):
			contexto = "Formato de CHAT ID invalido"
			return contexto, False
		registro.telegram_chatID=list(valor.values())[0]
	elif campo == 'passwd':
		hashp, salt = registros.passwd_hash(list(valor.values())[0].encode('utf-8'))
		hash_b64= base64.b64encode(hashp).decode('utf-8')
		salt_b64 = base64.b64encode(salt).decode('utf-8')
		passwdhs = salt_b64+'-$$-'+hash_b64

		key_aes_web_service, nonce_web_service = operaciones_ws.regresar_pass_service(list(valor.values())[0].encode('utf-8'))
		passwd_web_service = base64.b64encode(os.urandom(16))
		passwd_cif_web_service = back_end.cifrar(passwd_web_service, key_aes_web_service, nonce_web_service)
		web_service_keys = base64.b64encode(nonce_web_service).decode('utf-8')+'-$$-'+base64.b64encode(passwd_cif_web_service).decode('utf-8')
		if operaciones_ws.actualizar_password(admin, passwd_web_service.decode('utf-8')):
			registro.passhash_admin = passwdhs
			registro.passcif_webservice = web_service_keys
		else:
			contexto = "Ocurrio un error en la actualizacion de la contraseña, intentelo mas tarde"
			return contexto, False
	registro.save()

def actualizar_campos_admin(registro, admin, lista, lista_campos):
	for modificar in lista:
		for campo in lista_campos:
			if list(modificar.keys())[0] == campo:
				actualizar_administrador(registro, admin, campo, modificar)
	return '', True

def actualizar_campos_server(registro, lista):
	if len(lista) == 1: 
		if list(lista[0].keys())[0] == 'user':
			registro.user_servidor=list(lista[0].values())[0]
		elif list(lista[0].keys())[0] == 'pass':
			registro.passcif_servidor=list(lista[0].values())[0]
		registro.save()
	else:
		registro.user_servidor=list(lista[0].values())[0]
		registro.passcif_servidor=list(lista[1].values())[0]
		registro.save()
	return True
