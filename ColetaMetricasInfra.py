from paramiko import SSHClient
import paramiko
import time, datetime
import requests
import sys
import fileinput
import urllib2


SEP='|'

def influx_parse(metrica, sis_nm, tier, server, total, etime):
    url = 'http://brtlvlts0956fu:8086/write?db=metricas&precision=s'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = metrica+",Server=" + str (server) + ",sistema=" + str (sis_nm) + ",camada=" + str (tier) + " Total=" + str (
        total) + " " + str (etime)
    r = requests.post (url, data=payload, headers=headers)
    print(payload)

def influx_parse_load(sis_nm, tier, server, load1,load5,load15,etime):
    url = 'http://brtlvlts0956fu:8086/write?db=metricas&precision=s'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "LOADAVERAGE,Server=" + str (server) + ",sistema=" + str (sis_nm) + ",camada=" + str (tier) + " Load1=" + str (load1) + " " + str (etime)
    r = requests.post (url, data=payload, headers=headers)
    print(payload)
    payload = "LOADAVERAGE,Server=" + str (server) + ",sistema=" + str (sis_nm) + ",camada=" + str (tier) + " Load5=" + str (load5) + " " + str (etime)
    r = requests.post (url, data=payload, headers=headers)
    print (payload)
    payload = "LOADAVERAGE,Server=" + str (server) + ",sistema=" + str (sis_nm) + ",camada=" + str (tier) + " Load15=" + str (load15) + " " + str (etime)
    r = requests.post (url, data=payload, headers=headers)
    print (payload)



def writeLog(*args):
    d = datetime.datetime.strftime (datetime.datetime.now (), '%Y-%m-%d %H:%M:%S.%f')
    flgd = datetime.datetime.strftime (datetime.datetime.now (), '%Y-%m-%d_%H_%M_%S.%f')

    logfile = '/home/capacity/coletas/err/MonitoramentoServidores.log'

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
            msg = '[ERRO] Problemas ao SSH Servidor: ' + self.ip + ' - Sistema: ' + sis_nm
            writeLog (msg, e)

    def exec_cmd(self, cmd, metrica):
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

                if metrica in ['CPU','QTDE_CPU','QTDE_MEMORIA','SWAP_SERVER']:
		    teste = teste.split (' ')
                    Total = float (teste[0])
                    influx_parse (metrica,sis_nm, tier, server, Total, Epoch)

                if metrica == 'MEMORIA':
		    teste = teste.replace(',','.')
                    teste = teste.split (' ')
                    Total = float (teste[0])
                    influx_parse (metrica,sis_nm, tier, server, Total, Epoch)

                if metrica == 'LOAD':
                    teste = teste.replace ('/', ' ')
                    teste = teste.split (' ', 5)
                    Load1 = teste[0]
                    Load5 = teste[1]
                    Load15 = teste[2]
                    run = teste[3]
                    list = teste[4]
                    pid = teste[5]
                    influx_parse_load (sis_nm, tier, server, Load1, Load5, Load15, Epoch)


        except Exception as e:
            msg = '[ERRO] Problemas ao Comando Servidor: ' + self.ip + ' - Sistema: ' + sis_nm  + ' - Metrica: ' + metrica
            #print (msg)
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
     cAspasDuplas='"'
     cBar='\\'

     if(versaoLinux == "7") :

	 metrica="CPU"
         cComando="/usr/bin/vmstat 1 4|tail -3|awk '{ s+=100-$15 }END{ printf( "
         cComando=cComando+cAspasDuplas
         cComando=cComando+'%'
         cComando=cComando+".0f\\n"
         cComando=cComando+cAspasDuplas
         cComando=cComando+",s/NR )}'"
         ssh.exec_cmd (cComando,metrica)

	 metrica='MEMORIA';
	 ssh.exec_cmd ("free -m | grep 'Mem:' | awk '{ print ($3/$2)*100 }' ",metrica)

         metrica='LOAD';
         ssh.exec_cmd ("cat /proc/loadavg",metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
	 ssh.exec_cmd ("free -m  | grep 'Swap:' | awk ' { print ($3/$2)*100 } '",metrica)



     elif (versaoLinux == "AIX"):

	 metrica='CPU';
         ssh.exec_cmd ("vmstat 1 3 |tail -2 | head -1|awk '{print (100-$16)}'",metrica)

	 metrica='MEMORIA';
         cAspasDuplas = '"'
         cLineFeed = '\\n'
         comando = "VERAIX=`oslevel |cut -c 1` && if [ $VERAIX -eq 5 ]; then VAR1=`svmon` && echo $VAR1 "
         comando = comando + "|awk '{A=($14*4)/1024;B=($15*4)/1024;C=($7*4)/1024;D=($27*4)/1024;E=($29*4)/1024;F=($15*100)/$14;G=($27*100)/$7;H=($29*100)/$7} END "
         comando = comando + "{printf(" + cAspasDuplas + "%.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f"+cLineFeed+cAspasDuplas +",A,B,C,D,E,F,G,H)}'; else VAR1=`svmon -O unit=MB |sed 's/mmode//' |sed 's/Ded//' |sed 's/-//g'` && echo $VAR1 "
         comando = comando + "|awk '{A=$18;B=$19;C=$10;D=$31;E=$33;F=($19*100)/$18;G=($31*100)/$10;H=($33*100)/$10;} END {printf("+cAspasDuplas+"%.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f"+cLineFeed+cAspasDuplas+", A, B, C, D, E, F, G, H)}';fi|awk '{ print $7 }'"
         ssh.exec_cmd (comando,metrica)

         metrica='LOAD';
         cAspasDuplas = '"'
         comando = "uptime |head -1|awk " + "'{print $10,$11,$12}'"
         comando = comando + "|awk 'BEGIN {FS=" + cAspasDuplas + "," + cAspasDuplas +"}{print $1 $2 $3, "+cAspasDuplas+"1/1"+cAspasDuplas+" ',1'}'"
         ssh.exec_cmd ( comando,metrica )

         metrica='QTDE_CPU';
         ssh.exec_cmd ("cat /proc/cpuinfo | grep 'processor' | sort | uniq | wc -l",metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
         ssh.exec_cmd ("svmon |awk 'FNR == 3 {print (($4) / ($3))*100}'",metrica)


	
     elif (versaoLinux == "SOLARIS"):

	 metrica='CPU';
         ssh.exec_cmd ("vmstat 1 4 |tail -3 |awk '{cpu=cpu+$22} END{print int(100-(cpu/3))}'",metrica)

	 metrica='MEMORIA';
         ssh.exec_cmd ("MEM_TOT=`/usr/sbin/prtconf |grep Mem |awk '{print $3}'`;MEM_FREE=`vmstat 1 7|awk '{print $5}'|tail -5|awk '{s+=$1} END {print s/NR/1024}'`;PAGE_SIZE=`pagesize`;echo | awk 'BEGIN { print(('$MEM_TOT'-'$MEM_FREE')/('$MEM_TOT'))*100}'",metrica)	 

         metrica='LOAD';
         cAspasDuplas = '"'
         comando = "uptime |head -1|awk " + "'{print $10,$11,$12}'"
         comando = comando + "|awk 'BEGIN {FS=" + cAspasDuplas + "," + cAspasDuplas +"}{print $1 $2 $3, "+cAspasDuplas+"1/1"+cAspasDuplas+" ',1'}'"
         #print (comando)
         ssh.exec_cmd (comando,metrica)

         metrica='QTDE_CPU';
         ssh.exec_cmd ("cat /proc/cpuinfo | grep 'processor' | sort | uniq | wc -l",metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
         ssh.exec_cmd ("/usr/sbin/swap -l | tail -1 | awk ' { print (1-($5/$4))*100 } '",metrica)


     elif (versaoLinux == "SOLARIS_ZFS"):

         metrica='CPU';
         ssh.exec_cmd ("vmstat 1 4 |tail -3 |awk '{cpu=cpu+$22} END{print int(100-(cpu/3))}'",metrica)

         metrica='MEMORIA';
         cAspasDuplas = '"'
         ssh.exec_cmd ("MEM_TOT=`/usr/sbin/prtconf |grep Mem |awk '{print $3}'`;MEM_FREE=`vmstat 1 7|awk '{print $5}'|tail -5|awk '{s+=$1} END {print s/NR/1024}'`;PAGE_SIZE=`pagesize`;ZFS=`kstat zfs::arcstats:size |grep size |awk '{printf  " + cAspasDuplas + "%.0f" + cAspasDuplas + ", $2/1024/1024}'`;echo | awk 'BEGIN { print(('$MEM_TOT'-'$MEM_FREE'-'$ZFS')/('$MEM_TOT'))*100}'")

         metrica='LOAD';
         cAspasDuplas = '"'
         comando = "uptime |head -1|awk " + "'{print $10,$11,$12}'"
         comando = comando + "|awk 'BEGIN {FS=" + cAspasDuplas + "," + cAspasDuplas +"}{print $1 $2 $3, "+cAspasDuplas+"1/1"+cAspasDuplas+" ',1'}'"
         ssh.exec_cmd (comando,metrica)

         metrica='QTDE_CPU';
         ssh.exec_cmd ("cat /proc/cpuinfo | grep 'processor' | sort | uniq | wc -l",metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
         ssh.exec_cmd ("/usr/sbin/swap -l | tail -1 | awk ' { print (1-($5/$4))*100 } '",metrica)


	
     elif (versaoLinux == "HPUX"):

	 metrica='CPU';
         ssh.exec_cmd ("vmstat 1 3 |tail -2 | head -1|awk '{print (100-$18)}'",metrica)

         metrica='MEMORIA';
         comando="SLAB_MEM=\"$(cat /proc/meminfo | grep -i slab | awk '{print $2}')\" && USED_MEM=\"$(free -k | grep '\+ buffers' | awk '{print $3}')\" && TOTAL_MEM=\"$(free -k | grep 'Mem' | awk '{print $2}')\" && echo \( $USED_MEM - $SLAB_MEM \) \* 100  \/ $TOTAL_MEM | bc"
         ssh.exec_cmd (comando,metrica)

         metrica='LOAD';
         ssh.exec_cmd ("cat /proc/loadavg",metrica)

         metrica='QTDE_CPU';
         ssh.exec_cmd ("cat /proc/cpuinfo | grep 'processor' | sort | uniq | wc -l",metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
         ssh.exec_cmd ("free -m  | grep 'Swap:' | awk ' { print ($3/$2)*100 } '",metrica)


     elif (versaoLinux == "TERADATA"):

	 metrica='CPU';
         ssh.exec_cmd ("cat /serv_capacidade/TERADATA/results/cpu.txt",metrica)

     elif (versaoLinux == "TDVM"):

         metrica='CPU';
         ssh.exec_cmd ("cat /serv_capacidade/TERADATA/results/cpu_tdvm.txt",metrica)


     elif (versaoLinux == "BIGDATA"):

	 metrica='CPU';
         cComando="ssh capacity@"+server+" -q "
         cComando=cComando+"vmstat 1 4|tail -3|awk '{ s+=100-$15 }END{ printf( "
         cComando=cComando+cAspasDuplas
         cComando=cComando+'%'
         cComando=cComando+".0f\\n"
         cComando=cComando+cAspasDuplas
         cComando=cComando+",s/NR )}'"
         ssh.exec_cmd (cComando,metrica)

         metrica='MEMORIA';
         if (server == "serrano"):
	     comando="SLAB_MEM=\"$(ssh capacity@"+server+" -q cat /proc/meminfo | grep -i slab | awk '{print $2}')\" && USED_MEM=\"$(ssh capacity@"+server+" -q free -k | grep '\+ buffers' | awk '{print $3}')\" && TOTAL_MEM=\"$(ssh capacity@"+server+" -q free -k | grep 'Mem' | awk '{print $2}')\" && echo \( $USED_MEM - $SLAB_MEM \) \* 100  \/ $TOTAL_MEM | bc"
             ssh.exec_cmd (comando,metrica)
	 else:    
             ssh.exec_cmd ("ssh capacity@"+server+" -q free -m | grep 'Mem:' | awk '{ print ($3/$2)*100 }' ",metrica)

         metrica='LOAD';
         ssh.exec_cmd ("ssh capacity@"+server+" -q cat /proc/loadavg ",metrica)

         metrica='QTDE_CPU';
         ssh.exec_cmd ("ssh capacity@"+server+" -q cat /proc/cpuinfo | grep 'processor' | sort | uniq | wc -l" ,metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("ssh capacity@"+server+" -q cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
         ssh.exec_cmd ("ssh capacity@"+server+" -q free -m  | grep 'Swap:' | awk ' { print ($3/$2)*100 } ' ",metrica)


     else :

	 metrica='CPU';
         cComando="vmstat 1 4|tail -3|awk '{ s+=100-$15 }END{ printf( "
         cComando=cComando+cAspasDuplas
         cComando=cComando+'%'
         cComando=cComando+".0f\\n"
         cComando=cComando+cAspasDuplas
         cComando=cComando+",s/NR )}'"
         ssh.exec_cmd (cComando,metrica)

         metrica='MEMORIA';
         comando="SLAB_MEM=\"$(cat /proc/meminfo | grep -i slab | awk '{print $2}')\" && USED_MEM=\"$(free -k | grep '\+ buffers' | awk '{print $3}')\" && TOTAL_MEM=\"$(free -k | grep 'Mem' | awk '{print $2}')\" && echo \( $USED_MEM - $SLAB_MEM \) \* 100  \/ $TOTAL_MEM | bc"
         ssh.exec_cmd (comando,metrica)

         metrica='LOAD';
         ssh.exec_cmd ("cat /proc/loadavg",metrica)

         metrica='QTDE_CPU';
         ssh.exec_cmd ("cat /proc/cpuinfo | grep 'processor' | sort | uniq | wc -l",metrica)

         metrica='QTDE_MEMORIA';
         ssh.exec_cmd ("cat /proc/meminfo | grep 'MemTotal' |awk '{print($2)}'",metrica)

         metrica='SWAP_SERVER';
         ssh.exec_cmd ("free -m  | grep 'Swap:' | awk ' { print ($3/$2)*100 } '",metrica)

