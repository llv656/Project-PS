from django.template import Template, Context
from django.shortcuts import render, redirect
from ingreso import models
from adminServ.decoradores import *
from adminServ import operaciones_ws, servicio_admin, servicio_server
from collections import namedtuple
import adminServ.inicio_sesion as back_end
import adminServ.registro as registros
import subprocess
import os, base64

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
		codigo = codigo_multifactor('h')
		subprocess.call([path_alerta, TOKEN_TELEGRAM, CHAT_ID, 'Codigo de verificacion:'+' '+codigo])
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
				token_servers, llave_aes_token, nonce_token = operaciones_ws.start_session_service_web(usuario_admin, paswd_admin)
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
		info_monitoreo_servers = operaciones_ws.return_info_server(usuario_admin.decode('utf-8'), token_servers.decode('utf-8'))
		#interactuar con el template para mostar informacion 
		c = {'monitor_servers':info_monitoreo_servers}
		return render(request, t, c)

@esta_logueadoA
def server_connect(request):
	if request.method == 'POST':
		usuario_admin, token_servers = back_end.unwrap_tokens(request)
		credenciales_server = operaciones_ws.regresar_credenciales(usuario_admin)

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
		telegram_chatID = request.POST.get('telegram_chatID', None)
		passwdP = request.POST.get('password', ' ')
		vacio = ''
		if request.POST.get('crear', None) == 'crear':
			if user == vacio or nombre == vacio or apellidos == vacio or telegram_token == vacio or telegram_chatID == vacio or passwdP == vacio:
				return render(request, t, {'registroAd': ' ', 'errores': 'Todos los campos deben ser completados.'})
			registro_administrador = registros.registroADMIN(user, nombre, apellidos, telegram_token, telegram_chatID, passwdP)
			if registro_administrador[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroAd': ' ', 'errores': registro_administrador[0]}) #Error en el registro
		elif request.POST.get('actualizar', None) == 'actualizar':
			lista_modificaciones = []
			if user != vacio:
				if nombre != vacio or apellidos != vacio or telegram_token != vacio or telegram_chatID != vacio or passwdP != vacio:
					datos = {'nombre': nombre, 'apellidos': apellidos, 'telegram_t': telegram_token, 'telegram_i': telegram_chatID, 'passwd': passwdP}
					for valor in datos:
						if datos.get(valor.__str__()) != None and datos.get(valor.__str__()) != '':
							lista_modificaciones.append({valor: datos.get(valor)})

					actualizacion = servicio_admin.modificar_administrador(user, lista_modificaciones, lista_campos=list(datos.keys()))
					if actualizacion[1]:
						return redirect('/bienvenida_admin')
					else:
						return render(request, t, {'registroAd': ' ', 'errores': actualizacion[0]})
				else:
					return render(request, t, {'registroAd': ' ', 'errores': 'Se debe modificar al menos un campo'})
			else:
				return render(request, t, {'registroAd': ' ', 'errores': 'Se debe especificar el usuario a modificar'})
		elif request.POST.get('eliminar', None) == 'eliminar':
			if not user == '' or user == None:
				eliminar = servicio_admin.eliminar_administrador(user)
				if eliminar[1]:
					return redirect('/bienvenida_admin')
				else:
					return render(request, t, {'registroAd': ' ', 'errores': eliminar[0]})
			else:
				return render(request, t, {'registroAd': ' ', 'errores': 'Se debe especificar el usuario a eliminar'})

@esta_logueado
def registro_servidores(request):
	t = 'admin/bienvenidaAdmin.html'
	if request.method == 'GET':
		return render(request, t, {'registroSe': ' '})
	if request.method == 'POST':
#		if servicio_server.verificar_IP(request.POST.get('IP_server', None)):
		serverIP = request.POST.get('IP_server', None)
#		else:
#			return render(request, t, {'registroSe': ' ', 'errores': 'Ingrese una IP valida'})
		user_server = request.POST.get('user_server', None)
		pass_server = request.POST.get('pass_server', None)
		vacio=''
		if request.POST.get('crear_s', None) == 'crear_s':
			if user_server == vacio or pass_server == vacio:
				return render(request, t, {'registroSe': ' ', 'errores': 'Todos los campos deben ser completados.'}) 

			registro_servidor = registros.registroSERVER(serverIP, user_server, pass_server)
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

			actualizacion = servicio_server.modificar_servidor(serverIP, lista_modificaciones)
			if actualizacion[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroSe': ' ', 'errores': actualizacion[0]})
			#verificar existencia
			#al menos un campo deber ser completado
		elif request.POST.get('eliminar_s', None) == 'eliminar_s':
			eliminar = servicio_server.eliminar_servidor(serverIP)
			if eliminar[1]:
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'registroSe': ' ', 'errores': eliminar[0]})
			#verificar existencia
			#se elimina el servidor en la BD y en el API administrador

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
#		if not servicio_server.verificar_IP(ip_server):
#			return render(request, t, {'asociacion': ' ', 'errores': 'Ingrese una IP valida.'})
		if not servicio_server.existencia_servidor(ip_server):
			return render(request, t, {'asociacion': ' ', 'errores': 'Servidor no registrado'}) #, no es posible crear asociacion.'})
		if not servicio_admin.existencia_administrador(user_admin):
			return render(request, t, {'asociacion': ' ', 'errores': 'Administrador no registrado'}) #, no es posible crear asociacion.'})

		#Se crea asociacion, lo de arriba solo es verificacion
		if request.POST.get('crear_as', None) == 'crear_as':
			asociaciones = operaciones_ws.datos_asociaciones(ip_server)
			if not asociaciones and not asociaciones.__repr__() == '[]':
				return render(request, t, {'asociacion': ' ', 'errores': 'No fue posible realizar asociacion, intentelo mas tarde.'})
			if operaciones_ws.verificar_asociacion(asociaciones, ip_server):
				return render(request, t, {'asociacion': ' ', 'errores': 'Servidor ya asociado, no es posible crear asociacion.'})
			else:
				if operaciones_ws.asociar_servidores(user_admin, ip_server):
					return redirect('/bienvenida_admin')
				else:
					return render(request, t, {'asociacion': ' ', 'errores': 'Error en el registro de la asociacion, intentelo mas tarde.'})
		#verificar existencia del administrador y servidor
		#verificar si servidor se encuentra ya asociado
		elif request.POST.get('eliminar_as', None) == 'eliminar_as':
			if operaciones_ws.eliminar_server(ip_server):
				return redirect('/bienvenida_admin')
			else:
				return render(request, t, {'asociacion': ' ', 'errores': 'Error para eliminar asociacion, intente mas tarde.'})
		#solo se elimina el servidor de la asociacion en el API

@esta_logueado
def logout(request):
	request.session.flush()
	respuesta = redirect('/login')
	return respuesta

@esta_logueadoA
def logoutA(request):
	usuario_admin, token_servers = back_end.unwrap_tokens(request)
	request.session.flush()
	respuesta = redirect('/login')
	respuesta.delete_cookie('key1')
	respuesta.delete_cookie('key2')
	respuesta.delete_cookie('keyx')
	respuesta.delete_cookie('keyy')
	return respuesta
