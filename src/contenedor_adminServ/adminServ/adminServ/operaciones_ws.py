from adminServ import inicio_sesion as back_end
from adminServ import registro as registros
from adminServ import servicio_admin
from urllib.request import urlopen
from registroA import models
import adminServ.settings as VE
import urllib3, requests
import os, base64  
import json
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

urllib3.disable_warnings()

def regresar_pass_service(passwd_bin):
	nonce = os.urandom(16)
	if len(passwd_bin) == 32:
		return passwd_bin, nonce
	elif len(passwd_bin) < 32:
		bits = (32 - len(passwd_bin))*b'$'
		new_passwd = passwd_bin + bits
	elif len(passwd_bin) > 32:
		diferencia = len(passwd_bin)-32
		new_passwd = passwd_bin[:-diferencia]
	return new_passwd, nonce

def registro_web_service(user, passwd):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	data={'username': user, 'password': passwd}
	url_service = VE.URL_SERVICE+'/admin_recordAPI/'
	try:
		solicitud = requests.post(url_service, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error en registro en el API administrador')
		return False

def asociar_servidores(user_admin, ip_server):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	data={'username': user_admin, 'server_ip': ip_server}
	url_service = VE.URL_SERVICE + '/asociar_API/'
	try:
		solicitud = requests.post(url_service, headers=headers, data=data, verify=False)
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
	passwd_web_service = registros.decrypt(passwd_web_serviceCIF_b, keyAES_web_service, nonce_web_service_b)

	token_service = back_end.regresar_token(usuario.decode('utf-8'), passwd_web_service.decode('utf-8'))
	url_service = VE.URL_SERVICE + '/admin_sesionE/'
	headers={'Authorization': 'Token %s' % token_service}
	try:
		solicitud = requests.get(url_service, headers=headers, verify=False)
		lista_tokens = solicitud.json()['token_sessions']
		cadena=''
#		if len(lista_tokens) == 1:
#			cadena=lista_tokens[0]
#		else:
		for token in lista_tokens:
			logging.info(token)
			cadena=cadena+token+'$$$'
		cadena=cadena[:-3]
		llave, nonce = back_end.generar_llave()
		tokens_cifrado = back_end.cifrar(cadena.encode('utf-8'), llave, nonce)
		return base64.b64encode(tokens_cifrado).decode('utf-8'), base64.b64encode(llave).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')
	except:
		return False

def delete_session_service_web():
	pass

def return_info_server(usuario, token_servers):
	list_token  = token_servers.split('$$$')
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	url_infoAPI = VE.URL_SERVICE + '/info_serversAPI/'
	headers = {'Authorization': 'Token %s' % token_service}
	data = {'username': usuario, 'tokens_sessions': list_token}
#	data = json.dumps(data)
	try:
		respuesta = requests.post(url_infoAPI, headers=headers, data=data, verify=False)
		return respuesta.json()
	except:
		return False

def actualizar_password(user, passwd):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	data={'username': user, 'password': passwd}
	url_service = VE.URL_SERVICE+'/admin_recordAPI/'
	try:
		solicitud = requests.put(url_service, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error durante el registro en el API administrador')
		return False

def eliminar_admin(admin):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	data={'username': admin}
	url_service = VE.URL_SERVICE+'/admin_recordAPI/'
	try:
		solicitud = requests.delete(url_service, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error para eliminar al administrador en el API administrador')
		return False

def eliminar_server(ip_server):
        token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
        headers={'Authorization': 'Token %s' % token_service}
        data={'server_ip': ip_server}
        url_service = VE.URL_SERVICE+'/asociar_API/'
        try:
                solicitud = requests.delete(url_service, headers=headers, data=data, verify=False)
                return True
        except BaseException:
                logging.exception('Error para eliminar al administrador en el API administrador')
                return False

def datos_asociaciones(ip_server):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers={'Authorization': 'Token %s' % token_service}
	url_service = VE.URL_SERVICE+'/listar_AS/'
	try:
		solicitud = requests.get(url_service, headers=headers, verify=False)
		return solicitud.json()
	except BaseException:
		logging.exception('Error para solicitar datos de asociaciones en el API administrador')
		return False

def verificar_asociacion(asociaciones, ip_server):
	for asociacion in asociaciones:
		if len(list(asociacion.values())[1]) == 1:
			if list(asociacion.values())[1][0] == ip_server:
				return True
		else:
			for lista in list(asociacion.values())[1]:
				if lista == ip_server:
					return True
		return False
