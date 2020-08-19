from registroA import models
import adminServ.settings as VE
import os, base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import hashlib
from adminServ import inicio_sesion as back_end
from adminServ import servicio_admin, operaciones_ws
from datetime import datetime
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def timestamp():
	return datetime.now()

def passwd_hash(texto):
	salt=os.urandom(16)
	val_Hash = hashlib.sha256(salt+texto).digest()
	return val_Hash, salt

def decrypt(texto_cif, llave, nonce):
	aes_Cipher = Cipher(algorithms.AES(llave), modes.CTR(nonce), backend=default_backend())
	descifrador = aes_Cipher.decryptor()
	plano = descifrador.update(texto_cif)
	descifrador.finalize()
	return plano

def alerta_multifactor(request):
	aes_usr_b64 = request.COOKIES.get('key1', '')
	nonce_usr_b64 = request.COOKIES.get('key2', '')
	usuario_cif_b64 = request.session.get('usuario', '')

	aes_usr = base64.b64decode(aes_usr_b64)
	nonce_usr = base64.b64decode(nonce_usr_b64)

	usuario_cif = base64.b64decode(usuario_cif_b64.encode('utf-8'))
	usuario = decrypt(usuario_cif, aes_usr, nonce_usr)
	registro = models.Administradores.objects.get(user_admin=usuario.decode('utf-8'))
	token_telegram = registro.telegram_token
	chat_ID_telegram = registro.telegram_chatID
	
	return token_telegram, chat_ID_telegram

def verificar_passwdHash(user, passwdh):
	try:
		registro = models.Administradores.objects.get(user_admin=user)
		passh_validar = registro.passhash_admin #recupera dato de la columna del objeto de la tabla de la BD
		salt = base64.b64decode(passh_validar.split('-$$-')[0])
		passh_registro = base64.b64decode(passh_validar.split('-$$-')[1])
		new_passh=hashlib.sha256(salt+passwdh.encode('utf-8')).digest()
		if new_passh == passh_registro:
			return True
		else:
			return False
	except:
		return False

def registro_administrador(user, nombre, apellidos, telegram_token, telegram_id, passwd):
	hashp, salt = passwd_hash(passwd.encode('utf-8'))
	hash_b64= base64.b64encode(hashp).decode('utf-8')
	salt_b64 = base64.b64encode(salt).decode('utf-8')
	passwdhs = salt_b64+'-$$-'+hash_b64

	key_aes_web_service, nonce_web_service = operaciones_ws.regresar_pass_service(passwd.encode('utf-8'))
	passwd_web_service = base64.b64encode(os.urandom(16))
	passwd_cif_web_service = back_end.cifrar(passwd_web_service, key_aes_web_service, nonce_web_service)
	web_service_keys = base64.b64encode(nonce_web_service).decode('utf-8')+'-$$-'+base64.b64encode(passwd_cif_web_service).decode('utf-8')
	try:
		if operaciones_ws.registro_web_service(user, passwd_web_service.decode('utf-8')):
			registro_admin = models.Administradores(user_admin=user, 
								nombre=nombre, 
								apellidos=apellidos, 
								telegram_token=telegram_token, 
								telegram_chatID=telegram_id, 
								passhash_admin=passwdhs, 
								passcif_webservice=web_service_keys
								)
			registro_admin.save()
			return '', True
		else:
			contexto="Error en el registro en el API del administrador"
			return contexto, False
	except:
		contexto="Administrador ya registrado"
		return contexto, False

def registro_servidor(ip_server, user_server, pass_server):
	key_aes, nonce_pass = operaciones_ws.regresar_pass_service(VE.SECRET_PASSM.encode('utf-8'))
	passwd_cif = back_end.cifrar(pass_server.encode('utf-8'), key_aes, nonce_pass)
	passwd_sec = base64.b64encode(nonce_pass).decode('utf-8')+'-$$-'+base64.b64encode(passwd_cif).decode('utf-8')

	nonce_usr = os.urandom(16)
	user_cif = back_end.cifrar(user_server.encode('utf-8'), key_aes, nonce_usr)
	user_sec = base64.b64encode(nonce_usr).decode('utf-8')+'-$$-'+base64.b64encode(user_cif).decode('utf-8')

	try:
		models.Servidores.objects.get(ip=ip_server)
		contexto="Servidor ya registrado"
		return contexto, False
	except:
		try:
			registro_server = models.Servidores(user_servidor=user_sec, ip=ip_server, passcif_servidor=passwd_sec)
			registro_server.save()
			return '', True
		except BaseException:
			logging.exception('Error en registro de la base de datos')
			contexto="No se pudo realizar el registro en la Base de Datos"
			return contexto, False
