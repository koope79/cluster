# Рабочий - принимает нераспознанные аудиофайлы, распознаёт и передаёт ответ на сервер
import socket
import logging
from subprocess import run, STDOUT, PIPE

file_log = logging.FileHandler("client.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | CLIENT_2]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

# main_port
_port = 9093
_addr = '192.168.88.252'


def recognition(file_name):
    cmd = 'cd /home/rock64/pocketsphinx-5prealpha/ && export LD_LIBRARY_PATH=/usr/local/lib && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig && cd src/programs && pocketsphinx_continuous -samprate 16000 -hmm /home/rock64/pocketsphinx-5prealpha/model/ru-model/zero_ru.cd_cont_4000 -jsgf /home/rock64/nikolayDC/cluster/gram/cl2/cl2_gram.gram -dict /home/rock64/nikolayDC/cluster/gram/cl2/raw_cl2.dict -infile {} -logfn /dev/null'.format(file_name)
    output = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
    out_str = output.stdout.rstrip()

    if len(out_str) != 0:
        send_result(out_str)


def listen_tempo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect((_addr, 9091))
    sock.send('client_work'.encode())
    file_name = "/home/rock64/nikolayDC/cluster/CLIENT_AUDIO.wav"
    file = open(file_name, "wb")
    while True:
        data = sock.recv(4096)
        file.write(data)
        if not data:
            file.close()
            logging.info("CLIENT GOT FILE")
            #cmd = 'cd /home/rock64/nikolayDC/cluster/ && du -sh {}'.format(file_name)
            #out = run(cmd, stdout=PIPE, stderr=STDOUT, text=True, shell=True)
            #out_str = out.stdout.rstrip()
            #logging.info("FILE_SIZE: {}".format(out_str))
            recognition(file_name)
            break
            
    sock.close()

def my_start():
    logging.info("START Client!")
    listen_tempo()

def send_result(result):
    sock = socket.socket()
    sock.connect((_addr, _port))
    sock.send(result.encode())
    sock.close()
    logging.info("SENDED_RESULT")

my_start()
