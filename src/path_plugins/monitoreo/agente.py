import logging
import subprocess
import threading
import os
import json

PATH_LOGS=os.environ.get('PATH_LOGS')

def check_mem():
	use_mem = subprocess.check_output('free -m -h -t | grep T | awk \'{usage=($3*100)/$2} END {print usage}\'', shell=True).decode('utf-8').split()
	memoria= float(''.join(use_mem))
	if memoria > 75:
		subprocess.run(['bash','telegram.sh', 'Porcentaje de Memoria elevada: '+' '+str(memoria)+'%'])
		logging.warning('memoria: '+str(memoria)+ '%')
	else:
		logging.info('memoria: '+str(memoria)+'%')

def check_proc():
	use_proc = subprocess.check_output('grep \'cpu \' /proc/stat | awk \'{usage=($2+$4)*100/($2+$4+$5)} END {print usage}\'', shell=True).decode('utf-8').split()
	procesador = float(''.join(use_proc))
	if procesador > 75:
		subprocess.run(['bash','~/Documentos/PS/git/src/backend-PPS/monitoreo/telegram.sh', 'Porcentaje de Procesador elevado: '+' '+str(procesador)+'%'])
		logging.warning('procesador: '+str(procesador)+'%')
	else:
		logging.info('procesador: '+str(procesador)+'%')

def check_disk():
	use_disk = subprocess.check_output('df -h | grep -oP "[a-zA-Z0-9/]+[\ ]+[0-9.A-Z]+[\ ]+[0-9.A-Z]*[\ ]+[0-9.A-Z]+[\ ]+\K([0-9]+)"', shell=True).decode('utf-8').split()
	porcentaje=0
	for n in range(len(use_disk)):
		porcentaje = porcentaje+int(use_disk[n])
	if porcentaje > 75:
		subprocess.run(['bash','~/Documentos/PS/git/src/backend-PPS/monitoreo/telegram.sh', 'Porcentaje de Disco elevado'+' '+str(porcentaje)+'%'])
		logging.warning('Disco: '+str(porcentaje)+'%')
	else:
		logging.info('Disco: '+str(porcentaje)+'%')

if __name__ == '__main__':
	logging.basicConfig(filename=PATH_LOGS, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
	hiloP = threading.Thread(target=check_proc,).start()
	hiloM = threading.Thread(target=check_mem,).start()
	hiloD = threading.Thread(target=check_disk,).start()
