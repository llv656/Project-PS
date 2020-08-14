from ingreso import models
import datetime
import adminServ.settings as settings
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import requests
import urllib3
from urllib.request import urlopen
import json
from adminServ import settings
import adminServ.registro as registros

urllib3.disable_warnings()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def dejar_pasar_peticion_login(request):
    ip = get_client_ip(request)
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    try:
        registro = models.IPs.objects.get(ip=ip)
    except: # la ip nunca ha hecho peticiones
        nuevoRegistroIP = models.IPs(ip=ip, ultima_peticion=timestamp, intentos=1)
        nuevoRegistroIP.save()
        return True
    diferencia = (timestamp - registro.ultima_peticion).seconds
    if diferencia > settings.VENTANA_TIEMPO_INTENTOS_LOGIN:
        registro.ultima_peticion = timestamp
        registro.intentos=1
        registro.save()
        return True
    elif settings.INTENTOS_LOGIN > registro.intentos:
        registro.ultima_peticion = timestamp
        registro.intentos = registro.intentos+1
        registro.save()
        return True
    else:
        registro.ultima_peticion = timestamp
        registro.intentos = registro.intentos+1
        registro.save()
        return False

def cifrar(mensaje, llave, nonce):
    aesCipher = Cipher(algorithms.AES(llave), modes.CTR(nonce), backend=default_backend())
    cifrador = aesCipher.encryptor()
    cifrado = cifrador.update(mensaje)
    cifrador.finalize()
    return cifrado

def generar_llave():
    llave = os.urandom(16)
    iv = os.urandom(16)
    return llave, iv

def wrap_llaves(request, usuario, password):
    llave_aes_usr, iv_usr = generar_llave()
    llave_aes_passwd, iv_passwd = generar_llave()
    usuario_cifrado=cifrar(usuario.encode('utf-8'), llave_aes_usr, iv_usr)
    password_cifrado=cifrar(password.encode('utf-8'), llave_aes_passwd, iv_passwd)
    request.session['usuario'] = base64.b64encode(usuario_cifrado).decode('utf-8')
    request.session['password'] = base64.b64encode(password_cifrado).decode('utf-8')
    return (base64.b64encode(llave_aes_usr).decode('utf-8'), 
        base64.b64encode(iv_usr).decode('utf-8'), 
        base64.b64encode(llave_aes_passwd).decode('utf-8'), 
        base64.b64encode(iv_passwd).decode('utf-8')
        )

def regresar_token(username, passwd):
    data={'username': username,'password': passwd}
    url_service = settings.URL_SERVICE + '/autenticacion/'
    token_service = requests.post(url_service, data=data, verify=False)
    return token_service.json()['token']

def unwrap_llaves(request):
    llave_aes_usr_b64 = request.COOKIES.get('key1', '')
    iv_usr_b64 = request.COOKIES.get('key2', '')
    llave_aes_pwd_b64 = request.COOKIES.get('key3', '')
    iv_pwd_b64 = request.COOKIES.get('key4', '')
    usuario_cif_b64 = request.session.get('usuario', '')
    pwd_cif_b64 = request.session.get('password', '') 
    usuario_cif = base64.b64decode(usuario_cif_b64.encode('utf-8'))
    pwd_cif = base64.b64decode(pwd_cif_b64)
    llave_aes_usr = base64.b64decode(llave_aes_usr_b64.encode('utf-8'))
    llave_aes_pwd = base64.b64decode(llave_aes_pwd_b64.encode('utf-8'))
    iv_usr = base64.b64decode(iv_usr_b64.encode('utf-8'))
    iv_pwd = base64.b64decode(iv_pwd_b64.encode('utf-8'))
    usuario = registros.decrypt(usuario_cif, llave_aes_usr, iv_usr)
    pwd = registros.decrypt(pwd_cif, llave_aes_pwd, iv_pwd)
    return usuario, pwd

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
