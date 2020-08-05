from django.template import Template, Context
from django.shortcuts import render, redirect
from ingreso import models
from adminServ.decoradores import *
import adminServ.inicio_sesion as back_end
import adminServ.registro as registros
import subprocess
import os
import base64
import time
from collections import namedtuple

Codigo_SESION = namedtuple('Codigo_SESION', 'codigo')
csesion={}
csesion['codigo_multifactor'] = Codigo_SESION(codigo=None)

def login(request):
	t = 'login.html'
	if request.method == 'GET' and request.session.get('autenticadoA', False):
		return redirect('/multifactorA')
	if request.method == 'GET' and request.session.get('logueadoA', False):
		return redirect('/bienvenida_adminA')
	if request.method == 'GET' and not request.session.get('autenticado', False):
		if request.COOKIES.get('key1'):
			request.session.flush()
			respuesta = redirect('/login')
			respuesta.delete_cookie('key1')
			respuesta.delete_cookie('key2')
			respuesta.delete_cookie('key3')
			respuesta.delete_cookie('key4')
			return respuesta
		errores = request.session.get('errores', None)
		request.session['errores'] = None
		return render(request, t, {'autenticacion': ' '})
	elif request.method == 'GET':
        	return redirect('/multifactor')
	elif request.method == 'POST' and not request.session.get('autenticado', False):
		if back_end.dejar_pasar_peticion_login(request):
			usuario = request.POST.get('usuario', '')
			contra = request.POST.get('password', '')
			if os.environ.get('SECRET_USRM') == usuario and os.environ.get('SECRET_PASSM') == contra:
				respuesta = redirect('/multifactor')
				request.session['autenticado'] = True
				request.session.set_expiry(60)
				return respuesta
			elif registros.verificar_passwdHash(usuario, contra):
				respuesta = redirect('/multifactorA')
				llave_aes_usr, iv_usr, llave_aes_passwd, iv_passwd= back_end.wrap_llaves(request, usuario, contra)
				respuesta.set_cookie('key1', llave_aes_usr, httponly=True, samesite='Strict')
				respuesta.set_cookie('key2', iv_usr, httponly=True, samesite='Strict')
				respuesta.set_cookie('key3', llave_aes_passwd, httponly=True, samesite='Strict')
				respuesta.set_cookie('key4', iv_passwd, httponly=True, samesite='Strict')
				request.session['autenticadoA'] = True
				request.session.set_expiry(60)
				return respuesta
			else:
				return render(request, t, {'autenticacion': ' ', 'errores': 'Verifique sus credenciales.'})
		else:
			return render(request, t, {'autenticacion': ' ', 'errores': 'Demasiados intentos, debe esperar.'})

def codigo_multifactor(ver):
	codigo=str(int.from_bytes(os.urandom(2), byteorder='big')).encode('utf-8')
	if ver == 'h':
		csesion['codigo_multifactor'] = csesion.get('codigo_multifactor')._replace(codigo=codigo)
		return codigo.decode('utf-8')
	elif ver == 'f':
		contenido=csesion.get('codigo_multifactor').codigo
		return contenido.decode('utf-8')

@dos_pasos
def multifactor(request):
	t = 'login.html'
	if request.method == 'GET' and not request.session.get('logueado', False):
		path_alerta = base64.b64decode(os.environ.get('PATH_ALERTA'))
		TOKEN_TELEGRAM = base64.b64decode(os.environ.get('TOKEN_TELEGRAM'))
		CHAT_ID = base64.b64decode(os.environ.get('CHAT_ID'))
		subprocess.call([path_alerta, TOKEN_TELEGRAM, CHAT_ID, 'Codigo de verificacion:'+' '+codigo_multifactor('h')])
		return render(request, t, {'multifactor': ' '})
	elif request.method == 'GET' and request.session.get('logueadoA', ):
		return redirect('/bienvenida_adminA')
	elif request.method == 'GET':
		return redirect('/bienvenida_admin')
	elif request.method == 'POST':
		if back_end.dejar_pasar_peticion_login(request):
			codigo = request.POST.get('codigo', ' ')
			if codigo == codigo_multifactor('f'):
				csesion['codigo_multifactor'] = csesion.get('codigo_multifactor')._replace(codigo=None)
				respuestaM = redirect('/bienvenida_admin')
				request.session['logueado'] = True
				request.session.set_expiry(9200)
				return respuestaM
			else:
				return render(request, t, {'multifactor': ' ', 'errores': 'Codigo de verificacion no coincide'})
		else:
			return render(request, t, {'multifactorA': ' ', 'errores': 'Demasiados intentos fallidos.'})

@esta_logueado
def bienvenida_admin(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'bienvenidaAd': ' '})

@dos_pasosA
def multifactorA(request):	
	t = 'login.html'
	if request.method == 'GET' and not request.session.get('logueadoA', False):
		token_telegram, chatID_telegram = registros.alerta_multifactor(request)
		path_alerta=base64.b64decode(os.environ.get('PATH_ALERTA'))
		subprocess.call([path_alerta, token_telegram, chatID_telegram, 'Codigo de verificacion:'+' '+codigo_multifactor('h')])
		return render(request, t, {'multifactorA': ' '})
	elif request.method == 'GET':
		return redirect('/bienvenida_adminA')
	elif request.method == 'POST':
		if back_end.dejar_pasar_peticion_login(request):
			codigo = request.POST.get('codigo', ' ') 
			if codigo == codigo_multifactor('f'):
				#solicitar tokens servidores
				usuario_admin, paswd_admin = back_end.unwrap_llaves(request)
				token_servers, llave_aes_token, nonce_token = registros.start_session_service_web(usuario_admin, paswd_admin)
				#eliminar password del admin
				respuestaM = redirect('/bienvenida_adminA')
				respuestaM.delete_cookie('key3')
				respuestaM.delete_cookie('key4')
				del request.session['password']
				#almacenar nueva cookie de tokens de acceso a los servidores y la sesion
				respuestaM.set_cookie('keyx', llave_aes_token, httponly=True, samesite='Strict')
				respuestaM.set_cookie('keyy', nonce_token, httponly=True, samesite='Strict')
				request.session['tokens_sessions'] = token_servers
				request.session['logueadoA'] = True 
				request.session.set_expiry(9200)
				return respuestaM
			else:
				return render(request, t, {'multifactorA': ' ', 'errores': 'Codigo de verificacion no coincide'})
		else:
			return render(request, t, {'multifactorA': ' ', 'errores': 'Demasiados intentos fallidos.'})

@esta_logueadoA
def bienvenida_adminA(request):
	t = 'adminS/bienvenidaAdminSERV.html'
	if request.method == 'GET':
		#recuperar tokens de acceso y pasar en formato json al monitor administradorAPI
		usuario_admin, token_servers = back_end.unwrap_tokens(request)
		#recuperar la informacion
		info_monitoreo_servers = registros.return_info_server(usuario_admin.decode('utf-8'), token_servers.decode('utf-8'))
		#interactuar con el template para mostar informacion 
		c = {'monitor_servers':info_monitoreo_servers}
		return render(request, t, c)

@esta_logueado
def registro_administradores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'registroAd': ' '})
	elif request.method == 'POST':
		user = request.POST.get('usuario', None)
		nombre = request.POST.get('nombre', None)
		apellidos = request.POST.get('apellidos', None)
		telegram_token = request.POST.get('telegram_token', None)
		telegram_chatID = request.POST.get('telegram_chatID', None)
		passwdP = request.POST.get('password', ' ')
		vacio = ''
		if nombre == vacio or apellidos == vacio or telegram_token == vacio or telegram_chatID == vacio or passwdP == vacio:
			return render(request, t, {'registroAd': ' ', 'errores': 'Todos los campos deben ser completados.'}) 
		elif registros.registroADMIN(user, nombre, apellidos, telegram_token, telegram_chatID, passwdP):
			return redirect('/bienvenida_admin')
		else:
			return render(request, t, {'registroAd': ' ', 'errores': 'Administrador ya registrado.'}) #Error en el registro
	elif request.method == 'PUT':
		#verificar existencia
		#almenos un campo debe ser completado
		#si la contraseña se actualiza se debe de actualizar tambien la contraseña cifrada del API web service
		pass
	elif request.method == 'DELETE':
		#verificar existencia
		# se elimina el administrador de la BD y en el API el administrador y todos los servidores asociados
		pass

@esta_logueado
def registro_servidores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'registroSe': ' '})
	if request.method == 'POST':
		serverIP = request.POST.get('IP_server', None)
		user_server = request.POST.get('user_server', None)
		pass_server = request.POST.get('pass_server', None)
		vacio=''
		if serverIP == vacio or user_server == vacio or pass_server == vacio:
			return render(request, t, {'registroSe': ' ', 'errores': 'Todos los campos deben ser completados.'}) 
		elif registros.registroSERVER(serverIP, user_server, pass_server):
			return redirect('/bienvenida_admin')
		else:
			return render(request, t, {'registroSe': ' ', 'errores': 'Servidor ya registrado'})
	if request.method == 'PUT':
		#verificar existencia
		#al menos un campo deber ser completado
		pass
	if request.method == 'DELETE':
		#verificar existencia
		#se elimina el servidor en la BD y en el API administrador
		pass

@esta_logueado
def asociarAS(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'asociacion': ' '})
	elif request.method == 'POST':
		user_admin = request.POST.get('usuario_admin', None)
		ip_server = request.POST.get('IP_server', None)
		vacio=''
		if ip_server == vacio or user_admin == vacio:
			return render(request, t, {'asociacion': ' ', 'errores': 'Ambos campos deben ser completados.'})
		#verificar existencia del administrador y servidor
		#verificar si servidor se encuentra ya asociado
		elif registros.asociar_servidores(user_admin, ip_server):
			return redirect('/bienvenida_admin')
		else:
			return render(request, t, {'asociacion': ' ', 'errores': 'Error en el registro de la asociacion, intentelo mas tarde.'})
	elif request.method == 'DELETE':
		#solo se elimina el servidor de la asociacion en el API
		pass

@esta_logueado
def logout(request):
	request.session.flush()
	respuesta = redirect('/login')
	return respuesta

@esta_logueadoA
def logoutA(request):
	request.session.flush()
	respuesta = redirect('/login')
	respuesta.delete_cookie('key1')
	respuesta.delete_cookie('key2')
	respuesta.delete_cookie('keyx')
	respuesta.delete_cookie('keyy')
	return respuesta