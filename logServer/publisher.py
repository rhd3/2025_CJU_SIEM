# publisher.py
import socketserver
import pika
import time
import re

# RabbitMQ 설정 (RabbitMQ가 중앙 로그 서버에 설치되어 있다고 가정)
rabbitmq_host = 'localhost'  # 또는 RabbitMQ 서버의 IP 주소
rabbitmq_queue = 'syslog_logs'
rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = rabbit_conn.channel()
channel.queue_declare(queue=rabbitmq_queue)

def parse_syslog(message):
    try:
        decoded = message.decode('utf-8', errors='ignore')
    except Exception:
        decoded = str(message)
    # Cisco syslog 형식 예시: <PRI>Month Day HH:MM:SS device message
    pattern = r'<(\d+)>(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(.*)'
    match = re.match(pattern, decoded)
    if match:
        pri = int(match.group(1))
        timestamp = match.group(2)
        device = match.group(3)
        msg = match.group(4)
        severity_num = pri % 8
        severity_map = {
            0: "EMERGENCY", 1: "ALERT", 2: "CRITICAL", 3: "ERROR",
            4: "WARNING", 5: "NOTICE", 6: "INFO", 7: "DEBUG"
        }
        severity = severity_map.get(severity_num, "UNKNOWN")
        return timestamp, device, severity, msg
    else:
        return time.strftime("%b %d %H:%M:%S"), "unknown", "INFO", decoded

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        timestamp, device, severity, msg = parse_syslog(data)
        # 예: 로그를 SQLite에 저장
        cursor.execute('INSERT INTO syslogs (timestamp, device, severity, message) VALUES (?, ?, ?, ?)',
                       (timestamp, device, severity, msg))
        conn.commit()
        # 발행할 메시지 문자열 구성
        log_entry = f"{timestamp} {device} {severity}: {msg}"
        # RabbitMQ 큐에 로그 메시지 발행
        channel.basic_publish(exchange='',
                              routing_key=rabbitmq_queue,
                              body=log_entry)
        print(f"발행된 로그: {log_entry}")

if __name__ == "__main__":
    UDP_IP = "0.0.0.0"
    UDP_PORT = 514  # syslog 기본 포트
    server = socketserver.UDPServer((UDP_IP, UDP_PORT), SyslogUDPHandler)
    print(f"Syslog 서버가 {UDP_IP}:{UDP_PORT}에서 대기 중...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("종료합니다.")
        server.shutdown()
        conn.close()
        rabbit_conn.close()
