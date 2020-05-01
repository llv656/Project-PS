import threading
import subprocess

def check_MEM():
	useMem = subprocess.check_output('free -m -h -t | grep T | awk \'{usage=($3*100)/$2} END {print usage}\'', shell=True).decode('utf-8').split()
	print ('Uso de memoria     (%):', ''.join(useMem))

def check_PROC():
	useProc = subprocess.check_output('grep \'cpu \' /proc/stat | awk \'{usage=($2+$4)*100/($2+$4+$5)} END {print usage}\'', shell=True).decode('utf-8').split()
	print ('Uso de procesador  (%):', ''.join(useProc))

def check_DISK():
	useDisk = subprocess.check_output('df -h | grep -oP "[a-zA-Z0-9/]+[\ ]+[0-9.A-Z]+[\ ]+[0-9.A-Z]*[\ ]+[0-9.A-Z]+[\ ]+\K([0-9]+)"', shell=True).decode('utf-8').split()
	porcentajeD=0
	for n in range(len(useDisk)):
		porcentajeD = porcentajeD+int(useDisk[n])
	print ('Uso de disco       (%):', porcentajeD)

if __name__ == '__main__':
	hiloP = threading.Thread(target=check_PROC,).start()
	hiloM = threading.Thread(target=check_MEM,).start()
	hiloD = threading.Thread(target=check_DISK,).start()
