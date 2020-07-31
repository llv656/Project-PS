from registroA import models
import datetime
import adminServ.settings as VE
import os
import base64
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib
from adminServ import inicio_sesion as back_end
import requests

def passwdHash(texto):
	salt=os.urandom(16)
	valHash = hashlib.sha256(salt+texto).digest()
	return valHash, salt

def decrypt(texto_cif, llave, nonce):
	aesCipher = Cipher(algorithms.AES(llave), modes.CTR(nonce), backend=default_backend())
	descifrador = aesCipher.decryptor()
	plano = descifrador.update(texto_cif)
	descifrador.finalize()
	return plano

def alerta_multifactor(request):
	aes_usr_b64 = request.COOKIES.get('key1', '')
	nonce_usr_b64 = request.COOKIES.get('key2', '')
	usuario_cif_b64 = request.session.get('usuario', '')

	aes_usr = base64.b64decode(aes_usr_b64) #[2:-1])
	nonce_usr = base64.b64decode(nonce_usr_b64)

	usuario_cif = base64.b64decode(usuario_cif_b64.encode('utf-8'))
	usuario = decrypt(usuario_cif, aes_usr, nonce_usr)
	registro = models.Administradores.objects.get(user_admin=usuario.decode('utf-8'))
	token_telegram = registro.telegram_token
	chatID_telegram = registro.telegram_chatID
	
	return token_telegram, chatID_telegram

def regresar_pass_service(passwd_bin):
	nonce = os.urandom(16)
	if len(passwd_bin) == 32:
		return passwd_bin, nonce
	if len(passwd_bin) < 32:
		bits = (32 - len(passwd_bin))*b'$'
		new_passwd = passwd_bin + bits
	elif len(passwd_bin) > 32:
		diferencia = len(passwd_bin)-32
		new_passwd = passwd_bin[:-diferencia]
	return new_passwd, nonce

def verificar_passwdHash(user, passwdh):
	registro = models.Administradores.objects.get(user_admin=user)
	passh_validar = registro.passhash_admin #recupera dato de la columna del objeto de la tabla de la BD
	salt = base64.b64decode(passh_validar.split('-$$-')[0])
	passh_registro = base64.b64decode(passh_validar.split('-$$-')[1])
	new_passh=hashlib.sha256(salt+passwdh.encode('utf-8')).digest()
	if new_passh == passh_registro:
		return True
	else:
		return False

def registro_web_service(user, passwd):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	data={'username': user, 'password': passwd}
	url_service = VE.URL_SERVICE+'/admin_recordAPI/'
	try:
		solicitud = requests.post(url_service, headers=headers, data=data)
		return True
	except:
		return False

def registroADMIN(user, nombre, apellidos, telegramT, telegramI, passwd):
	hashp, salt = passwdHash(passwd.encode('utf-8'))
	hashB64= base64.b64encode(hashp).decode('utf-8')
	saltB64 = base64.b64encode(salt).decode('utf-8')
	passwdhs = saltB64+'-$$-'+hashB64

	keyAES_web_service, nonce_web_service = regresar_pass_service(passwd.encode('utf-8'))
	passwd_web_service = base64.b64encode(os.urandom(16))
	passwdCIF_web_service = back_end.cifrar(passwd_web_service, keyAES_web_service, nonce_web_service)
	web_serviceKEYS = base64.b64encode(nonce_web_service).decode('utf-8')+'-$$-'+base64.b64encode(passwdCIF_web_service).decode('utf-8')
	if registro_web_service(user, passwd_web_service.decode('utf-8')):
		registroAd = models.Administradores(user_admin=user, nombre=nombre, apellidos=apellidos, telegram_token=telegramT, telegram_chatID=telegramI, passhash_admin=passwdhs, passcif_webservice=web_serviceKEYS)
		registroAd.save()
		return True
	else:
		return False

def registroSERVER(serverIP, user_server, pass_server):
	keyAES_USR, nonce_USR = regresar_pass_service(VE.USR_SERVICE.encode('utf-8'))
	passwd_cif = back_end.cifrar(pass_server.encode('utf-8'), keyAES_USR, nonce_USR)
	passwd_sec = base64.b64encode(nonce_USR).decode('utf-8')+'-$$-'+base64.b64encode(passwd_cif).decode('utf-8')

	nonce_USR = os.urandom(16)
	user_cif = back_end.cifrar(user_server.encode('utf-8'), keyAES_USR, nonce_USR)
	user_sec = base64.b64encode(nonce_USR).decode('utf-8')+'-$$-'+base64.b64encode(user_cif).decode('utf-8')

	registroSe = models.Servidores(user_servidor=user_sec, ip=serverIP, passcif_servidor=passwd_sec)
	registroSe.save()
	return True

def asociar_servidores(user_admin, ip_server):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	data={'username': user_admin, 'server_ip': ip_server}
	url_service = VE.URL_SERVICE + '/asociar_API/'
	try:
		solicitud = requests.post(url_service, headers=headers, data=data)
		return True
	except:
		return False

def start_session_service_web(usuario, password):
	registro = models.Administradores.objects.get(user_admin=usuario.decode('utf-8'))
	keyAES_web_service, nonce_default = regresar_pass_service(password)

	passcif_webservice = registro.passcif_webservice

	nonce_web_service = passcif_webservice.split('-$$-')[0]
	passwd_web_serviceCIF = passcif_webservice.split('-$$-')[1]

	nonce_web_service_b = base64.b64decode(nonce_web_service)
	passwd_web_serviceCIF_b = base64.b64decode(passwd_web_serviceCIF)
	passwd_web_service = decrypt(passwd_web_serviceCIF_b, keyAES_web_service, nonce_web_service_b)

	token_service = back_end.regresar_token(usuario.decode('utf-8'), passwd_web_service.decode('utf-8'))
	url_service = VE.URL_SERVICE + '/admin_sesionE/'
	headers={'Authorization': 'Token %s' % token_service}
	try:
		solicitud = requests.get(url_service, headers=headers)
		lista_tokens = solicitud.json()['token_sessions']
		cadena=''
#		for i in range(0, len(lista_tokens)-1):
#			cadena=cadena+lista_tokens[i]+'$$$'
#		cadena=cadena+lista_tokens[len(lista_tokens)]
#		print(cadena)
		
		llave, nonce = back_end.generar_llave()
		tokens_cifrado = back_end.cifrar(lista_tokens[0].encode('utf-8'), llave, nonce)
		return base64.b64encode(tokens_cifrado).decode('utf-8'), base64.b64encode(llave).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')
	except:
		return False

def return_info_server(usuario, token_servers):
	list_token  = token_servers.split('$$$')
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	url_infoAPI = VE.URL_SERVICE + '/info_serversAPI/'
	headers = {'Authorization': 'Token %s' % token_service}
	data = {'username': usuario, 'tokens_sessions': list_token}
	try:
		respuesta = requests.post(url_infoAPI, headers=headers, data=data)
		return respuesta.json()
	except:
		return False
