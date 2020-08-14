from adminServ import inicio_sesion as back_end
from adminServ import registro as registros
from adminServ import operaciones_ws
import os, base64

def actualizar_campos_admin(registro, admin, lista, lista_campos):
	if len(lista) == 1: 
		for campo in lista_campos:
			if list(lista[0].keys())[0] == campo:
				if campo == 'nombre':
					registro.nombre=list(lista[0].values())[0]
				elif campo == 'apellidos':
					registro.apellidos=list(lista[0].values())[0]
				elif campo == 'telegram_t':
					registro.telegram_token=list(lista[0].values())[0]
				elif campo == 'telegram_i':
					registro.telegram_chatID=list(lista[0].values())[0]
				elif campo == 'passwd':
					hashp, salt = registros.passwdHash(list(lista[0].values())[0].encode('utf-8'))
					hashB64= base64.b64encode(hashp).decode('utf-8')
					saltB64 = base64.b64encode(salt).decode('utf-8')
					passwdhs = saltB64+'-$$-'+hashB64

					keyAES_web_service, nonce_web_service = operaciones_ws.regresar_pass_service(list(lista[0].values())[0].encode('utf-8'))
					passwd_web_service = base64.b64encode(os.urandom(16))
					passwdCIF_web_service = back_end.cifrar(passwd_web_service, keyAES_web_service, nonce_web_service)
					web_serviceKEYS = base64.b64encode(nonce_web_service).decode('utf-8')+'-$$-'+base64.b64encode(passwdCIF_web_service).decode('utf-8')
					if operaciones_ws.actualizar_password(admin, passwd_web_service.decode('utf-8')):
						registro.passhash_admin = passwdhs
						registro.passcif_webservice = web_serviceKEYS
					else:
						contexto = "Ocurrio un error en la actualizacion de la contraña, intente mas tarde"
						return contexto, False
				registro.save()
				return '', True
	else:
		for i in range(len(lista)):
			for campo in lista_campos:
				if list(lista[i].keys())[0] == campo:
					if campo == 'nombre':
						registro.nombre=list(lista[i].values())[0]
					elif campo == 'apellidos':
						registro.apellidos=list(lista[i].values())[0]
					elif campo == 'telegram_t':
						registro.telegram_token=list(lista[i].values())[0]
					elif campo == 'telegram_i':
						registro.telegram_chatID=list(lista[i].values())[0]
					elif campo == 'passwd':
						hashp, salt = registros.passwdHash(list(lista[i].values())[0].encode('utf-8'))
						hashB64= base64.b64encode(hashp).decode('utf-8')
						saltB64 = base64.b64encode(salt).decode('utf-8')
						passwdhs = saltB64+'-$$-'+hashB64

						keyAES_web_service, nonce_web_service = operaciones_ws.regresar_pass_service(list(campo_registro.values())[0].encode('utf-8'))
						passwd_web_service = base64.b64encode(os.urandom(16))
						passwdCIF_web_service = back_end.cifrar(passwd_web_service, keyAES_web_service, nonce_web_service)
						web_serviceKEYS = base64.b64encode(nonce_web_service).decode('utf-8')+'-$$-'+base64.b64encode(passwdCIF_web_service).decode('utf-8')

						if operaciones_ws.actualizar_password(admin, passwd_web_service.decode('utf-8')):
							registro.passhash_admin = passwdhs
							registro.passcif_webservice = web_serviceKEYS
						else:
							contexto = "Ocurrio un error durante la actualizacion de la contraseña, intente mas tarde"
							return contexto, False
		registro.save()
		return '', True

def actualizar_campos_server(registro, lista):
	if len(lista) == 1: 
		if list(lista[0].keys())[0] == 'user':
			registro.user_servidor=list(lista[0].values())[0]
		elif list(lista[0].keys())[0] == 'pass':
			registro.passcif_servidor=list(lista[0].values())[0]
		registro.save()
		return True
	else:
		registro.user_servidor=list(lista[0].values())[0]
		registro.passcif_servidor=list(lista[1].values())[0]
		registro.save()
		return True
