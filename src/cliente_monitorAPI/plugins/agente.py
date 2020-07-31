import logging
import subprocess
import threading
import os
import json
from cliente_monitorAPI import settings

PATH_LOGS = settings.PATH_LOGS

def check_mem():
	use_mem = subprocess.check_output('free -m -h -t | grep T | awk \'{usage=(($3/1000)*100)/$2} END {print usage}\'', shell=True).decode('utf-8').split()
	memoria = float(''.join(use_mem))
	if memoria > 75:
		logging.warning('Memoria: '+str(memoria)+ '%')
	else:
		logging.info('Memoria: '+str(memoria)+'%')
	return str(memoria)+'%'

def check_proc():
	use_proc = subprocess.check_output('grep \'cpu \' /proc/stat | awk \'{usage=($2+$4)*1000/($2+$4+$5)} END {print usage}\'', shell=True).decode('utf-8').split()
	procesador = float(''.join(use_proc))
	if procesador > 75:
		logging.warning('Procesador: '+str(procesador)+'%')
	else:
		logging.info('Procesador: '+str(procesador)+'%')
	return str(procesador)+'%'

def check_disk():
	use_disk = subprocess.check_output('df -h | grep -oP "[a-zA-Z0-9/]+[\ ]+[0-9.A-Z]+[\ ]+[0-9.A-Z]*[\ ]+[0-9.A-Z]+[\ ]+\K([0-9]+)"', shell=True).decode('utf-8').split()
	porcentaje=0
	for n in range(len(use_disk)):
		porcentaje = porcentaje+int(use_disk[n])
	if porcentaje > 75:
		logging.warning('Disco: '+str(porcentaje)+'%')
	else:
		logging.info('Disco: '+str(porcentaje)+'%')
	return str(porcentaje)+'%'

def check_server():
	logging.basicConfig(filename=PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
	proc = check_proc()
	mem = check_mem()
	disk = check_disk()
	status_server={"procesador": proc, "memoria": mem, "disco": disk}
	return json.dumps(status_server)
