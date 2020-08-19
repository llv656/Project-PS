from adminServ import inicio_sesion as back_end
from adminServ import operaciones_ws
from adminServ import settings as VE
from adminServ.modificar import modificar_campos
from registroA import models
import os, base64
import logging

logging.basicConfig(filename=VE.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

def verificar_ip(ip_server):
	if len(ip_server.split('.')) == 4:
		pass
	else:
		return False
	for num in ip_server.split('.'):
		try:
			if int(num) > 0 and int(num) < 256:
				pass
			else:
				return False
		except:
			return False
	return True

def existencia_servidor(ip_server):
	try:
		models.Servidores.objects.get(ip=ip_server)
		return True
	except:
		return False
	
def modificar_servidor(ip_server, lista):
	try:
		registro = models.Servidores.objects.get(ip=ip_server)
		if modificar_campos.actualizar_campos_server(registro, lista):
			return '', True
		else:
			logging.error('Error al actualizar datos, servidor si existe')
			contexto="Ocurrio un error al querer actualizar los datos, intente mas tarde"
			return contexto, False
	except BaseException:
		logging.exception('Error al actualizar Servidor')
		contexto="Servidor no existe"
		return contexto, False

def eliminar_servidor(ip_server):
	try:
		registro = models.Servidores.objects.get(ip=ip_server)
		if operaciones_ws.eliminar_server(ip_server):
			registro.delete()
			return '', True
		else:
			contexto = "Ocurrio un error mientras se intentaba eliminar el servidor, intente mas tarde"
			return contexto, False
	except BaseException:
		logging.exception('Error al eliminar Servidor')
		contexto="Servidor no existe"
		return contexto, False
