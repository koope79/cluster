# Client_1 - распознаёт файлы и передаёт ответ серверу (файл или результата)

import socket
import logging
import time
from subprocess import run, STDOUT, PIPE

file_log = logging.FileHandler("client.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | CLIENT_1]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# main_port
_port = 9092
_addr = '192.168.88.252'

def recognition():
    for i in range(1, 31):
        start_time = time.time()
        name_file = '/home/rock64/nikolayDC/cluster/recs/test1/rec{}.wav'.format(i)
        cmd = 'cd /home/rock64/pocketsphinx-5prealpha/ && export LD_LIBRARY_PATH=/usr/local/lib && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && cd src/programs && pocketsphinx_continuous -samprate 16000 -hmm /home/rock64/pocketsphinx-5prealpha/model/ru-model/zero_ru.cd_cont_4000 -jsgf /home/rock64/nikolayDC/cluster/gram/cl1/cl1_gram.gram -dict /home/rock64/nikolayDC/cluster/gram/cl1/raw_cl1.dict -infile {} -logfn /dev/null'.format(name_file)
        output = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
        out_str = output.stdout.strip()

        if len(out_str) == 0:
            send_audio(name_file)
        else:
            com = 'sudo soxi -D {}'.format(name_file)
            output_com = run(com, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
            out_com = output_com.stdout.rstrip()
            send_result(out_str, start_time, out_com)
            
def my_start():
    logging.info("START Client1!")
    recognition()

def send_audio(name_file):
    sock = socket.socket()
    sock.connect((_addr, _port))
    file = open(name_file, "rb")
    while True:
        file_data = file.read(65536)
        sock.send(file_data)
        if not file_data:
            break
    sock.close()
    logging.info("File Sended")

def log_duration(start_time, out_com):
    f = open('/home/rock64/nikolayDC/cluster/log_dur.txt', 'a+')
    timer = time.time() - start_time
    f.write(str(timer) + " / " + str(out_com) + "\n")
    f.close()
    #logging.info("Time_reco: {}".format(time.time() - start_time))

def send_result(result, start_time, out_com):
    sock = socket.socket()
    sock.connect((_addr, _port))
    sock.send(result.encode())
    sock.close()
    log_duration(start_time, out_com)
    logging.info("SENDED1 RESULT")
    
my_start()


