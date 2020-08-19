from django.template import Template, Context
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponse
from ingreso import models
from adminServ.decoradores import *
from adminServ import operaciones_ws, servicio_admin, servicio_server
from collections import namedtuple
from adminServ import settings as VE
import adminServ.inicio_sesion as back_end
import adminServ.registro as registros
import subprocess
import os, base64
import json
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

Codigo_SESION = namedtuple('Codigo_SESION', 'codigo')
csesion={}
csesion['codigo_multifactor'] = Codigo_SESION(codigo=None)

def login(request):
	t = 'login.html'
	if request.method == 'GET' and request.session.get('autenticadoA', False):
		return redirect('/multifactor_administrador')
	if request.method == 'GET' and request.session.get('logueadoA', False):
		return redirect('/bienvenida_administrador_servidores')
	if request.method == 'GET' and not request.session.get('autenticado', False):
		if request.COOKIES.get('key1'):
			request.session.flush()
			respuesta = redirect('/login')
			respuesta.delete_cookie('key1')
			respuesta.delete_cookie('key2')
			return respuesta
		if back_end.verificar_lista_negra(request):
			return HttpResponse(status=401)
		return render(request, t, {'autenticacion': ' '})
	elif request.method == 'GET':
		return redirect('/multifactor')
	elif request.method == 'POST' and not request.session.get('autenticado', False):
		if back_end.verificar_lista_negra(request):
			return HttpResponse(status=401)
		if not back_end.dejar_pasar_peticion_login(request):
			return render(request, t, {'autenticacion': ' ', 'errores': 'Demasiados intentos, debe esperar.'})
		usuario = request.POST.get('usuario', '')
		contra = request.POST.get('password', '')
		lista_negra_caracteres = servicio_admin.CARACTERES_ESPECIALES
		longitud_min = servicio_admin.MIN_LONG_USER
		longitud_max = servicio_admin.MAX_LONG_USER
		if not servicio_admin.verificar_campo(usuario, lista_negra_caracteres, longitud_min, longitud_max):
			return render(request, t, {'autenticacion': ' ', 'errores': 'Ingrese un nombre de usuario valido'})
		if os.environ.get('SECRET_USRM') == usuario and os.environ.get('SECRET_PASSM') == contra:
			respuesta = redirect('/multifactor')
			request.session['autenticado'] = True
			request.session.set_expiry(60)
			return respuesta
		elif registros.verificar_passwdHash(usuario, contra):
			respuesta = redirect('/multifactor_administrador')
			llave_aes_usr, iv_usr = back_end.wrap_llaves(request, usuario)
			respuesta.set_cookie('key1', llave_aes_usr, httponly=True, samesite='Strict')
			respuesta.set_cookie('key2', iv_usr, httponly=True, samesite='Strict')
			request.session['autenticadoA'] = True
			request.session.set_expiry(60)
			return respuesta
		else:
			return render(request, t, {'autenticacion': ' ', 'errores': 'Verifique sus credenciales.'})

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
		codigo = codigo_multifactor('h')
		subprocess.call([path_alerta, TOKEN_TELEGRAM, CHAT_ID, 'Codigo de verificacion:'+' '+codigo])
		return render(request, t, {'multifactor': ' '})
	elif request.method == 'GET' and request.session.get('logueadoA', ):
		return redirect('/bienvenida_administrador_servidores')
	elif request.method == 'GET':
		return redirect('/bienvenida_admin')
	elif request.method == 'POST':
		if not back_end.dejar_pasar_peticion_multifactor(request):
			return render(request, t, {'multifactorA': ' ', 'errores': 'Demasiados intentos fallidos.'})
		codigo = request.POST.get('codigo', ' ')
		codigo = codigo.strip()
		if codigo == codigo_multifactor('f'):
			back_end.login(request, 'Administrador Global')
			csesion['codigo_multifactor'] = csesion.get('codigo_multifactor')._replace(codigo=None)
			respuesta_multifactor = redirect('/bienvenida_admin')
			request.session['logueado'] = True
			request.session.set_expiry(18000)
			return respuesta_multifactor
		else:
			return render(request, t, {'multifactor': ' ', 'errores': 'Codigo de verificacion no coincide'})

@esta_logueado
def bienvenida_admin(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'bienvenidaAd': ' '})

@dos_pasos_administrador_servidores
def multifactor_administrador(request):
	t = 'login.html'
	if request.method == 'GET' and not request.session.get('logueadoA', False):
		token_telegram, chat_id_telegram = registros.alerta_multifactor(request)
		path_alerta=base64.b64decode(os.environ.get('PATH_ALERTA'))
		subprocess.call([path_alerta, token_telegram, chat_id_telegram, 'Codigo de verificacion:'+' '+codigo_multifactor('h')])
		return render(request, t, {'multifactorA': ' '})
	elif request.method == 'GET':
		return redirect('/bienvenida_administrador_servidores')
	elif request.method == 'POST':
		if back_end.dejar_pasar_peticion_login(request):
			codigo = request.POST.get('codigo', ' ') 
			codigo = codigo.strip()
			if codigo == codigo_multifactor('f'):
				#solicitar tokens servidores
				usuario_admin = back_end.unwrap_llaves(request)
				token_servers, llave_aes_token, nonce_token = operaciones_ws.start_session_service_web(usuario_admin)
				back_end.login(request, usuario_admin.decode('utf-8'))
				respuesta_multifactor = redirect('/bienvenida_administrador_servidores')
				respuesta_multifactor.set_cookie('keyx', llave_aes_token, httponly=True, samesite='Strict')
				respuesta_multifactor.set_cookie('keyy', nonce_token, httponly=True, samesite='Strict')
				request.session['tokens_sessions'] = token_servers
				request.session['logueadoA'] = True 
				request.session.set_expiry(18000)
				return respuesta_multifactor
			else:
				return render(request, t, {'multifactorA': ' ', 'errores': 'Codigo de verificacion no coincide'})
		else:
			return render(request, t, {'multifactorA': ' ', 'errores': 'Demasiados intentos fallidos.'})

@esta_logueado_administrador_servidores
def bienvenida_administrador_servidores(request):
	t = 'adminS/bienvenidaAdminSERV.html'
	if request.method == 'GET':
		usuario_admin, token_servers = back_end.unwrap_tokens(request)
		info_monitoreo_servers = operaciones_ws.return_info_server(usuario_admin.decode('utf-8'), token_servers.decode('utf-8'))
		c = {'monitor_servers':info_monitoreo_servers}
		return render(request, t, c)

@esta_logueado_administrador_servidores
def informacion_servidor(request):
	t = 'adminS/informacion.html'
	usuario_admin, token_servers = back_end.unwrap_tokens(request)
	info_monitoreo_servers = operaciones_ws.return_info_server(usuario_admin.decode('utf-8'), token_servers.decode('utf-8'))
	c = {'monitor_servers':info_monitoreo_servers}
	return render(request, t, c)

@esta_logueado
def registro_administradores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'registroAd': ' '})
	if request.method == 'POST':

		user = request.POST.get('usuario', None)
		nombre = request.POST.get('nombre', None)
		apellidos = request.POST.get('apellidos', None)
		telegram_token = request.POST.get('telegram_token', None)
		telegram_chat_id = request.POST.get('telegram_chatID', None)
		passwd_post = request.POST.get('password', ' ')
		vacio = ''

		if request.POST.get('crear', None) == 'crear':
			if user == vacio or nombre == vacio or apellidos == vacio or telegram_token == vacio or telegram_chat_id == vacio or passwd_post == vacio:
				return render(request, t, {'registroAd': ' ', 'errores': 'Todos los campos deben ser completados.'})
			verificar_campos = servicio_admin.verificar_campos_registro(user, nombre, apellidos, telegram_token, telegram_chat_id)
			if not verificar_campos[1]:
				return render(request, t, {'registroAd': ' ', 'errores': verificar_campos[0]})
			registro_administrador = registros.registro_administrador(user, nombre, apellidos, telegram_token, telegram_chat_id, passwd_post)
			if registro_administrador[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroAd': ' ', 'errores': registro_administrador[0]})
		elif request.POST.get('actualizar', None) == 'actualizar':
			lista_modificaciones = []
			if user == vacio:
				return render(request, t, {'registroAd': ' ', 'errores': 'Se debe especificar el usuario a modificar'})

			if nombre == vacio and apellidos == vacio and telegram_token == vacio and telegram_chat_id == vacio and passwd_post == vacio:
				return render(request, t, {'registroAd': ' ', 'errores': 'Se debe modificar al menos un campo'})

			datos = {'nombre': nombre, 'apellidos': apellidos, 'telegram_t': telegram_token, 'telegram_i': telegram_chat_id, 'passwd': passwd_post}
			for valor in datos:
				if datos.get(valor.__str__()) != None and datos.get(valor.__str__()) != '':
					lista_modificaciones.append({valor: datos.get(valor)})

			actualizacion = servicio_admin.modificar_administrador(user, lista_modificaciones, lista_campos=list(datos.keys()))
			if actualizacion[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroAd': ' ', 'errores': actualizacion[0]})
		elif request.POST.get('eliminar', None) == 'eliminar':
			if user == '':
				return render(request, t, {'registroAd': ' ', 'errores': 'Se debe especificar el usuario a eliminar'})
			lista_negra_caracteres = servicio_admin.CARACTERES_ESPECIALES
			longitud_min = servicio_admin.MIN_LONG_USER
			longitud_max = servicio_admin.MAX_LONG_USER
			if not servicio_admin.verificar_campo(user, lista_negra_caracteres, longitud_min, longitud_max):
				return render(request, t, {'registroAd': ' ', 'errores': 'Ingrese un nombre de usuario valido'})
			eliminar = servicio_admin.eliminar_administrador(user)
			if eliminar[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroAd': ' ', 'errores': eliminar[0]})
		elif request.POST.get('mostrar', None) == 'mostrar':
			return redirect('/mostrar_administradores')
		return HttpResponse(status=401)

@esta_logueado
def mostrar_administradores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		lista_administradores = servicio_admin.mostrar_administradores()
		return render(request, t, {'mostrarAd': ' ', 'administradores': lista_administradores})

@esta_logueado
def registro_servidores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'registroSe': ' '})
	if request.method == 'POST':

#		if servicio_server.verificar_ip(request.POST.get('IP_server', None)):
		ip_server = request.POST.get('IP_server', None)
#		else:
#			return render(request, t, {'registroSe': ' ', 'errores': 'Ingrese una IP valida'})
		user_server = request.POST.get('user_server', None)
		pass_server = request.POST.get('pass_server', None)
		vacio=''

		if request.POST.get('crear_s', None) == 'crear_s':
			if user_server == vacio or pass_server == vacio:
				return render(request, t, {'registroSe': ' ', 'errores': 'Todos los campos deben ser completados.'}) 
			registro_servidor = registros.registro_servidor(ip_server, user_server, pass_server)
			if registro_servidor[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroSe': ' ', 'errores': registro_servidor[0]})
		elif request.POST.get('actualizar_s', None) == 'actualizar_s':
			if user_server == vacio and pass_server == vacio:
				return render(request, t, {'registroSe': ' ', 'errores': 'Se debe modificar al menos un campo.'})

			datos = {'user': user_server, 'pass': pass_server}
			lista_modificaciones = []
			for valor in datos:
				if datos.get(valor.__str__()) != None and datos.get(valor.__str__()) != '':
					lista_modificaciones.append({valor: datos.get(valor)})

			actualizacion = servicio_server.modificar_servidor(ip_server, lista_modificaciones)
			if actualizacion[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroSe': ' ', 'errores': actualizacion[0]})
		elif request.POST.get('eliminar_s', None) == 'eliminar_s':
			eliminar = servicio_server.eliminar_servidor(ip_server)
			if eliminar[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroSe': ' ', 'errores': eliminar[0]})
		elif request.POST.get('mostrar_s', None) == 'mostrar_s':
			return redirect('/mostrar_servidores')
		return HttpResponse(status=401)

@esta_logueado
def mostrar_servidores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		lista_servidores = servicio_server.mostrar_servidores()
		return render(request, t, {'mostrarSe': ' ', 'servidores': lista_servidores})

@esta_logueado
def asociar_administrador_servidor(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'asociacion': ' '})
	elif request.method == 'POST':

		user_admin = request.POST.get('usuario_admin', None)
		ip_server = request.POST.get('IP_server', None)
		vacio=''
		if request.POST.get('mostrar_as', None) == 'mostrar_as':
                        return redirect('/mostrar_asociaciones')

		if ip_server == vacio or user_admin == vacio:
			return render(request, t, {'asociacion': ' ', 'errores': 'Ambos campos deben ser completados.'})
		lista_negra_caracteres = servicio_admin.CARACTERES_ESPECIALES
		longitud_min = servicio_admin.MIN_LONG_USER
		longitud_max = servicio_admin.MAX_LONG_USER
		if not servicio_admin.verificar_campo(user_admin, lista_negra_caracteres, longitud_min, longitud_max):
			return render(request, t, {'asociacion': ' ', 'errores': 'Ingrese un nombre de usuario valido'})
#		if not servicio_server.verificar_ip(ip_server):
#			return render(request, t, {'asociacion': ' ', 'errores': 'Ingrese una IP valida.'})
		if not servicio_server.existencia_servidor(ip_server):
			return render(request, t, {'asociacion': ' ', 'errores': 'Servidor no registrado'})
		if not servicio_admin.existencia_administrador(user_admin):
			return render(request, t, {'asociacion': ' ', 'errores': 'Administrador no registrado'})

		if request.POST.get('crear_as', None) == 'crear_as':
			asociaciones = operaciones_ws.datos_asociaciones()
			if not asociaciones and not asociaciones.__repr__() == '[]':
				return render(request, t, {'asociacion': ' ', 'errores': 'No fue posible realizar asociacion, intentelo mas tarde.'})
			if operaciones_ws.verificar_asociacion(asociaciones, ip_server):
				return render(request, t, {'asociacion': ' ', 'errores': 'Servidor ya asociado, no es posible crear asociacion.'})
			else:
				if operaciones_ws.asociar_servidores(user_admin, ip_server):
					return redirect('/bienvenida_admin')
				else:
					return render(request, t, {'asociacion': ' ', 'errores': 'Error en el registro de la asociacion, intentelo mas tarde.'})
		elif request.POST.get('eliminar_as', None) == 'eliminar_as':
			if operaciones_ws.eliminar_server(ip_server):
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'asociacion': ' ', 'errores': 'Error para eliminar asociacion, intente mas tarde.'})
		return HttpResponse(status=401)

@esta_logueado
def mostrar_asociaciones(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		asociaciones = operaciones_ws.datos_asociaciones()
		return render(request, t, {'mostrarAs': ' ', 'asociaciones': asociaciones})

@esta_logueado
def sesiones_administradores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		sesiones = back_end.sesion_administradores()
		return render(request, t, {'sesiones_administradores': ' ', 'sesiones': sesiones})

@esta_logueado
def logout(request):
	back_end.logout(request)
	request.session.flush()
	respuesta = redirect('/login')
	return respuesta

@esta_logueado_administrador_servidores
def logout_admin_server(request):
	usuario_admin, token_servers = back_end.unwrap_tokens(request)
	operaciones_ws.stop_session_service_web(usuario_admin.decode('utf-8'), token_servers.decode('utf-8'))
	back_end.logout(request)
	request.session.flush()
	respuesta = redirect('/login')
	respuesta.delete_cookie('key1')
	respuesta.delete_cookie('key2')
	respuesta.delete_cookie('keyx')
	respuesta.delete_cookie('keyy')
	return respuesta
