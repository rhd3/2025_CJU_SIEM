#socket 사용 버전

import socket
LOG_FILE = "/var/log/fortigate.log"
LOG_SERVER_IP = "10.0.0.3"
LOG_SERVER_PORT = 514

def send_log_to_server(log_data):
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.sento(log_data.encode(), (LOG_SERVER_IP, LOG_SERVER_PORT))
    socket.close()

def monitor_log():
    with open(LOG_FILE, "r") as file:
        file.seek(0.2)
        while True:
            line = file.readline()
            if not line:
                continue
            send_log_to_server(line.strip())


if__name__=="__main__":
    monitor_log()
