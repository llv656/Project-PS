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

logging.basicConfig(filename=VE.PATH_LOGS, 
			filemode='a', 
			format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
			level=logging.DEBUG
			)

urllib3.disable_warnings()

def regresar_encabezado(token):
	return {'Authorization': 'Token %s' % token}

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
	headers = regresar_encabezado(token_service)
	data={'username': user, 'password': passwd}
	url_service = VE.URL_SERVICE+'/api_administradores/'
	try:
		requests.post(url_service, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error en registro en el API administrador')
		return False

def asociar_servidores(user_admin, ip_server):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers = regresar_encabezado(token_service)
	data={'username': user_admin, 'server_ip': ip_server}
	url_service = VE.URL_SERVICE + '/api_asociar_servidores/'
	try:
		requests.post(url_service, headers=headers, data=data, verify=False)
		return True
	except:
		return False

def start_session_service_web(usuario):
	registro = models.Administradores.objects.get(user_admin=usuario.decode('utf-8'))

	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	url_service = VE.URL_SERVICE + '/session_ephemeral_admin/'
	headers = regresar_encabezado(token_service)
	data = {'username': usuario}
	try:
		solicitud = requests.post(url_service, headers=headers, data=data, verify=False)
		lista_tokens = solicitud.json()['token_sessions']
		cadena=''
		for token in lista_tokens:
			cadena=cadena+token+'$$$'
		cadena=cadena[:-3]
		llave, nonce = back_end.generar_llave()
		tokens_cifrado = back_end.cifrar(cadena.encode('utf-8'), llave, nonce)

		return base64.b64encode(tokens_cifrado).decode('utf-8'), base64.b64encode(llave).decode('utf-8'), base64.b64encode(nonce).decode('utf-8')
	except:
		return False

def stop_session_service_web(usuario, token_servers):
	list_token  = token_servers.split('$$$')
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	url_asociacion_efimera = VE.URL_SERVICE + '/session_ephemeral_admin/'
	headers = regresar_encabezado(token_service)
	data = {'username': usuario, 'tokens_sessions': list_token}
	try:
		respuesta = requests.delete(url_asociacion_efimera, headers=headers, data=data, verify=False)
		if respuesta.status_code == 200:
			return True
		else:
			logging.error('Ocurrio un error mientras se intentaba comunicar con la API de asociacion')
			logging.error('No se eliminaron los usuarios efimeros en el cliente')
			return False
	except:
		return False

def return_info_server(usuario, token_servers):
	list_token  = token_servers.split('$$$')
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	url_informacion_servidores = VE.URL_SERVICE + '/get_servers_info_api/'
	headers = regresar_encabezado(token_service)
	data = {'username': usuario, 'tokens_sessions': list_token}
	try:
		respuesta = requests.post(url_informacion_servidores, headers=headers, data=data, verify=False)
		return respuesta.json()
	except:
		return False

def actualizar_password(user, passwd):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers = regresar_encabezado(token_service)
	data={'username': user, 'password': passwd}
	url_registro_admin = VE.URL_SERVICE+'/api_administradores/'
	try:
		requests.put(url_registro_admin, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error durante el registro en el API administrador')
		return False

def eliminar_admin(admin):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers = regresar_encabezado(token_service)
	data={'username': admin}
	url_service = VE.URL_SERVICE+'/api_administradores/'
	try:
		requests.delete(url_service, headers=headers, data=data, verify=False)
		return True
	except BaseException:
		logging.exception('Error para eliminar al administrador en el API administrador')
		return False

def eliminar_server(ip_server):
        token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
        headers = regresar_encabezado(token_service)
        data={'server_ip': ip_server}
        url_service = VE.URL_SERVICE+'/api_asociar_servidores/'
        try:
                requests.delete(url_service, headers=headers, data=data, verify=False)
                return True
        except BaseException:
                logging.exception('Error para eliminar al administrador en el API administrador')
                return False

def datos_asociaciones(ip_server):
	token_service = back_end.regresar_token(VE.USR_SERVICE, VE.PASS_SERVICE)
	headers = regresar_encabezado(token_service)
	url_service = VE.URL_SERVICE+'/listar_asociaciones/'
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
