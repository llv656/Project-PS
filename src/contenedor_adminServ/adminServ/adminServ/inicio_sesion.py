from ingreso import models
import datetime
import adminServ.settings as settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os, base64
import requests
import urllib3
from urllib.request import urlopen
import json
from adminServ import settings
import adminServ.registro as registros
import logging

logging.basicConfig(filename=settings.PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
urllib3.disable_warnings()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def lista_negra(registro, timestamp, ip):
    registro.ultima_peticion = timestamp
    registro.intentos = registro.intentos+1
    
    if registro.total_intentos > 0:
        registro.total_intentos = registro.total_intentos+1
        if registro.total_intentos >= settings.TOTAL_INTENTOS:
            lista_negra = models.ListaNegra(ip=ip)
            lista_negra.save()
    else:
        registro.total_intentos = 1
    registro.save()

def dejar_pasar_peticion_login(request):
    ip = get_client_ip(request)
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    try:
        registro = models.IPs.objects.get(ip=ip)
    except:
        nuevo_Registro_IP = models.IPs(ip=ip, ultima_peticion=timestamp, intentos=1, intentos_multifactor=0, total_intentos=0)
        nuevo_Registro_IP.save()
        return True
    diferencia = (timestamp - registro.ultima_peticion).seconds
    if diferencia > settings.VENTANA_TIEMPO_INTENTOS_LOGIN:
        registro.ultima_peticion = timestamp
        registro.intentos = 1
        registro.save()
        return True
    elif settings.INTENTOS_LOGIN > registro.intentos:
        registro.ultima_peticion = timestamp
        registro.intentos = registro.intentos+1
        registro.save()
        return True
    else:
        lista_negra(registro, timestamp, ip)
        return False

def dejar_pasar_peticion_multifactor(request):
    ip = get_client_ip(request)
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    try:
        registro = models.IPs.objects.get(ip=ip)
    except:
        nuevo_Registro_IP = models.IPs(ip=ip, ultima_peticion=timestamp, intentos_multifactor=1)
        nuevo_Registro_IP.save()
        return True
    diferencia = (timestamp - registro.ultima_peticion).seconds
    if diferencia > settings.VENTANA_TIEMPO_INTENTOS_MULTIFACTOR:
        registro.ultima_peticion = timestamp
        registro.intentos_multifactor = 1
        registro.save()
        return True
    elif settings.INTENTOS_LOGIN > registro.intentos_multifactor:
        registro.ultima_peticion = timestamp
        registro.intentos_multifactor = registro.intentos_multifactor+1
        registro.save()
        return True
    else:
        registro.intentos_multifactor = registro.intentos_multifactor+1
        registro.save()
        return False

def verificar_lista_negra(request):
    ip = get_client_ip(request)
    try:
        models.ListaNegra.objects.get(ip=ip)
        return True
    except:
        return False

def login(request, usuario):
    id_sesion = base64.b64encode(os.urandom(16)).decode('utf-8')
    ip = get_client_ip(request)
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    sesion = models.Sesiones(id_sesion=id_sesion, usuario=usuario, login=timestamp, logout=timestamp, ip=ip)
    request.session['id_sesion'] = id_sesion
    sesion.save()
    return True

def logout(request):
    id_sesion = request.session.get('id_sesion', '')
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    try:
        sesion = models.Sesiones.objects.get(id_sesion=id_sesion)
    except BaseException:
        logging.exception('Error al recuperar la sesion del usuario')
        return False
    sesion.logout = timestamp
    sesion.save()
    return True

def cifrar(mensaje, llave, nonce):
    aes_Cipher = Cipher(algorithms.AES(llave), modes.CTR(nonce), backend=default_backend())
    cifrador = aes_Cipher.encryptor()
    cifrado = cifrador.update(mensaje)
    cifrador.finalize()
    return cifrado

def generar_llave():
    llave = os.urandom(16)
    iv = os.urandom(16)
    return llave, iv

def wrap_llaves(request, usuario):
    llave_aes_usr, iv_usr = generar_llave()
    usuario_cifrado=cifrar(usuario.encode('utf-8'), llave_aes_usr, iv_usr)
    request.session['usuario'] = base64.b64encode(usuario_cifrado).decode('utf-8')
    return (base64.b64encode(llave_aes_usr).decode('utf-8'), 
        base64.b64encode(iv_usr).decode('utf-8'), 
        )

def regresar_token(username, passwd):
    data={'username': username,'password': passwd}
    url_service = settings.URL_SERVICE + '/autenticacion/'
    token_service = requests.post(url_service, data=data, verify=False)
    return token_service.json()['token']

def unwrap_llaves(request):
    llave_aes_usr_b64 = request.COOKIES.get('key1', '')
    iv_usr_b64 = request.COOKIES.get('key2', '')
    usuario_cif_b64 = request.session.get('usuario', '')
    usuario_cif = base64.b64decode(usuario_cif_b64.encode('utf-8'))
    llave_aes_usr = base64.b64decode(llave_aes_usr_b64.encode('utf-8'))
    iv_usr = base64.b64decode(iv_usr_b64.encode('utf-8'))
    usuario = registros.decrypt(usuario_cif, llave_aes_usr, iv_usr)
    return usuario

def unwrap_tokens(request):
    llave_aes_usr_b64 = request.COOKIES.get('key1', '')
    iv_usr_b64 = request.COOKIES.get('key2', '')
    llave_aes_token_b64 = request.COOKIES.get('keyx', '')
    iv_token_b64 = request.COOKIES.get('keyy', '')
    usuario_cif_b64 = request.session.get('usuario', '')
    tokens_cif_b64 = request.session.get('tokens_sessions', '') 
    usuario_cif = base64.b64decode(usuario_cif_b64.encode('utf-8'))
    tokens_cif = base64.b64decode(tokens_cif_b64)
    llave_aes_usr = base64.b64decode(llave_aes_usr_b64.encode('utf-8'))
    llave_aes_token = base64.b64decode(llave_aes_token_b64.encode('utf-8'))
    iv_usr = base64.b64decode(iv_usr_b64.encode('utf-8'))
    iv_token = base64.b64decode(iv_token_b64.encode('utf-8'))
    usuario = registros.decrypt(usuario_cif, llave_aes_usr, iv_usr)
    tokens = registros.decrypt(tokens_cif, llave_aes_token, iv_token)
    return usuario, tokens

def sesion_administradores():
    lista = []
    lista_total_sesiones = list(models.Sesiones.objects.all())
    cadena = ''
    for sesion in lista_total_sesiones:
        login = sesion.login
        logout = sesion.logout
        datos = [
                    sesion.usuario, 
                    str(login.hour)+':'+str(login.minute)+':'+str(login.second),
                    str(logout.hour)+':'+str(logout.minute)+':'+str(logout.second)
                ]
        lista.append(datos)
    return lista
