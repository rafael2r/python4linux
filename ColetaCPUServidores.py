from paramiko import SSHClient
import paramiko
import time, datetime
import requests
import sys
import fileinput
import urllib2


SEP='|'
ref_arquivo = '/home/capacity/coletas/param/servidores_monitorados.txt'


def influx_parse(sis_nm, tier, server, total, etime):
    url = 'http://localhost:8086/write?db=metricas&precision=s'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "CPU,Server=" + str (server) + ",sistema=" + str (sis_nm) + ",camada=" + str (tier) + " Total=" + str (
        total) + " " + str (etime)
    r = requests.post (url, data=payload, headers=headers)
    print(payload)


def writeLog(*args):
    d = datetime.datetime.strftime (datetime.datetime.now (), '%Y-%m-%d %H:%M:%S.%f')
    flgd = datetime.datetime.strftime (datetime.datetime.now (), '%Y-%m-%d_%H_%M_%S.%f')

    logfile = '/home/capacity/coletas/err/coleta_metricas_cpu.log'

    if len (args) == 2:
        with open (logfile, 'a') as log:
            log.write ('[' + d + ']' + ' ' + args[0] + '. ' + str (args[1]) + '\n')
            print ('[' + d + ']' + ' ' + args[0] + '. ' + str (args[1]))
    else:
        with open (logfile, 'a') as log:
            log.write ('[' + d + ']' + ' ' + args[0] + '.' + '\n')
            print ('[' + d + ']' + ' ' + args[0])

class SSH:
    def __init__(self):
        try:
            self.ssh = SSHClient ()
            self.ssh.load_system_host_keys ()
            self.ssh.set_missing_host_key_policy (paramiko.AutoAddPolicy ())
            # DEFINE O HOST A CONECTAR
            self.ip = server
            # MONTA A STRING DE CONEXAO COM HOST, USUARIO E SENHA
            self.ssh.connect (self.ip, username=usr, password=pswd)
        except Exception as e:
            msg = '[ERRO] Problemas ao SSH Servidor ' + self.ip
            writeLog (msg, e)

    def exec_cmd(self, cmd):
        try:
            stdin, stdout, stderr = self.ssh.exec_command (cmd)
            if stderr.channel.recv_exit_status () != 0:
                print (stderr.read ())
            else:
                dia = datetime.datetime.now ().strftime ('%Y-%m-%dT%H:%M:%S')
                ts = time.strptime (dia, '%Y-%m-%dT%H:%M:%S')
                epochx = time.mktime (ts)
                Epoch = str (epochx)[:-2]
                teste = stdout.read ()
                teste = teste.split (' ')
                Total = float (teste[0])
                influx_parse (sis_nm, tier, server, Total, Epoch)
        except Exception as e:
            msg = '[ERRO] Problemas ao Comando Servidor ' + self.ip
            writeLog (msg, e)

parts=sys.argv[1].split(SEP) #RECEBE LINHA A LINHA DO ARQUIVO SERVIDORES.TXT
sis_nm = parts[0]
tier = parts[1]
server =  parts[2]
usr = parts[3]
pswd = parts[4]
versaoLinux = parts[5]

if __name__ == '__main__':
     ssh = SSH ()
     if(versaoLinux == "7") :
         ssh.exec_cmd ("vmstat 1 3 |tail -2 | head -1|awk '{print (100-$15)}'")
     else :
         ssh.exec_cmd ("vmstat 1 3 |tail -1 | head -1|awk '{print(100-$15)}' ")



