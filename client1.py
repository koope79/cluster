# Client_1 - распознаёт файлы и передаёт ответ серверу (файл или результата)

import socket
import logging
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
    for i in range(1,5):
        name_file = '/home/rock64/nikolayDC/cluster/recs/rec{}.wav'.format(i)
        cmd = 'cd /home/rock64/pocketsphinx-5prealpha/ && export LD_LIBRARY_PATH=/usr/local/lib && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && cd src/programs && pocketsphinx_continuous -samprate 16000 -hmm /home/rock64/pocketsphinx-5prealpha/model/ru-model/zero_ru.cd_cont_4000 -jsgf /home/rock64/nikolayDC/cluster/gram/cl1/cl1_gram.gram -dict /home/rock64/nikolayDC/cluster/gram/cl1/raw_cl1_dict -infile {} -logfn /dev/null'.format(name_file)
        output = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
        out_str = output.stdout.rstrip()

        if len(out_str) == 0:
            send_audio(name_file)
        else:
            send_result(out_str)
            
def my_start():
    logging.info("START Client1!")
    recognition()

def send_audio(name_file):
    sock = socket.socket()
    sock.connect((_addr, _port))
    file = open(name_file, "rb")
    while True:
        file_data = file.read(4096)
        sock.send(file_data)
        if not file_data:
            break
    sock.close()
    logging.info("File Sended")

def send_result(result):
    sock = socket.socket()
    sock.connect((_addr, _port))
    sock.send(result.encode())
    sock.close()
    logging.info("SENDED1 RESULT")
    
my_start()


