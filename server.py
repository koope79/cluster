# Сервер - держатель общих данных, он их отдает и сохраняет процессобезопасно

import logging
import socket
import multiprocessing
import time
import _thread

file_log = logging.FileHandler("server.log")
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s | SERVER]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

ports = []
scheduler_port = 9090

# общие данные
manager = multiprocessing.Manager()
result = manager.list()

th_lock = _thread.allocate_lock()
names_mas = manager.list()
count = None


def start_server(_ports, _users):
    global count
    ports = _ports
    count = _users
    time.sleep(1)
    listen(ports, count)

def threaded(conn, addr, file_name):
    global count
    file = open(file_name, "rb")
    while True:
        try:
            res = conn.recv(65536)
            if res.decode() == 'client_work':
                while True:
                    file_data = file.read(65536)
                    conn.send(file_data)
                    if not file_data:
                        file.close()
                        break
                    
                logging.info("FILE SENDED FROM TEMPO: {}".format(file_name))
                th_lock.acquire()
                count -= 1
                if count == 0:
                    names_mas.remove(file_name)
                th_lock.release()
                conn.close() 
                break
            
        except Exception as e:
            print(e)

# промежуточный порт, служащий для рассылки файлов
def tempo_port(ip, temp_port, circle):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, temp_port))
    sock.listen()
    logging.info("Started Tempo_Port {}!".format(temp_port))
    while True:
        global count
        conn, addr = sock.accept()
        #logging.info("Connected: " + str(addr))
        th_lock.acquire()
        if count == 0:
            count = circle
        th_lock.release()
        last_name_audio = names_mas[0]
        _thread.start_new_thread(threaded,(conn, addr, last_name_audio,))
        #logging.info("Connected close: " + str(addr))

def start_clients():
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('got_file_from_client'.encode())
    sock.close()  

# основной обработчик задач от клиентов
def listen_process(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    logging.info("Created server port {}!".format(port))
    sock.listen()
    i = 0
    while True:
        conn, addr = sock.accept()
        logging.info("Connected: " + str(addr))
        file_name = "/home/rock64/nikolayDC/cluster/SERVER_AUDIO_{}.wav".format(i)
        file = open(file_name, "wb")
        while True:
            global result
            data = conn.recv(65536)
            try:
                if data.decode():
                    logging.info("SERVER Command " + data.decode() + " from " + str(addr))
                    if len(data.decode()) < 100:
                        f = open('result.txt', 'a+')
                        f.write(data.decode() + '\n')
                        f.close()
                        result.append(data.decode())
                    logging.info("RESULTS_DATA: {}".format(result))
                    break
                    
            except Exception:
                file.write(data)
                
            finally:
                if not data:
                    logging.info("AUDIO FILE ON SERVER")
                    file.close()
                    i += 1
                    names_mas.append(file_name)
                    start_clients()
                    time.sleep(2)
                    #logging.info("RESULTS_DATA: {}".format(result))
                    break
                
        conn.close()

# запускаем на каждом порту в пуле прослушивание. Каждый порт слушает в отдельном процессе
def listen(ports, count):
    process = []
    for i in ports:
        main_process = multiprocessing.Process(target=listen_process, args=('', i))
        main_process.start()
        process.append(main_process)
        
    tempo_process = multiprocessing.Process(target=tempo_port, args=('', 9091, count,))
    tempo_process.start()
    process.append(tempo_process)

    # сообщаем планировщику, что все процессы запустились и можно продолжать работу
    sock = socket.socket()
    sock.connect(('', scheduler_port))
    sock.send('port_created'.encode())
    sock.close()
    for i in process:
        # ожидаем завершения процессов, иначе общие данные пропадут (Manager умирает при убивании основного процесса)
        i.join()

