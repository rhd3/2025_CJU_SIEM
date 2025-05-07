# [1] Suricata 로그 파서 (eve.json 기반)

import json
import pika
import os
import time
from datetime import datetime

RABBITMQ_HOST = "192.168.10.100"
LOG_FILE = "/var/log/suricata/eve.json"

def tail_file(filepath):
    with open(filepath, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                time.sleep(0.2)

def suricata_agent():
    for line in tail_file(LOG_FILE):
        try:
            data = json.loads(line.strip())
            entry = {
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "source": "suricata",
                "host": os.uname().nodename,
                "message": data.get("alert", {}).get("signature", "no signature"),
                "raw": data
            }
            send_to_rabbitmq(entry)
        except:
            continue

def send_to_rabbitmq(entry):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='logs', durable=True)
    channel.basic_publish(exchange='', routing_key='logs', body=json.dumps(entry))
    connection.close()


# [2] FortiGate 로그 파서 (rsyslog 연동 로그)

import re

def fortigate_agent(file_path):
    for line in tail_file(file_path):
        match = re.match(r"<\d+>(.+)", line)
        msg = match.group(1) if match else line.strip()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": "fortigate",
            "host": os.uname().nodename,
            "message": msg,
            "raw": line.strip()
        }
        send_to_rabbitmq(entry)


# [3] VPN 로그 파서 (/var/log/auth.log or openvpn.log)

def vpn_agent(file_path):
    for line in tail_file(file_path):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": "vpn",
            "host": os.uname().nodename,
            "message": line.strip(),
            "raw": line.strip()
        }
        send_to_rabbitmq(entry)


# [4] RabbitMQ 소비자 - 로그별 파일 저장용

import os
import json
import pika
from datetime import datetime

LOG_DIR = "./log_output"
os.makedirs(LOG_DIR, exist_ok=True)

def write_log_to_file(log):
    source = log.get("source", "unknown")
    ts = datetime.now().strftime("%Y-%m-%d")
    dir_path = os.path.join(LOG_DIR, source)
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{ts}.log")
    with open(file_path, "a") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

def file_consumer_callback(ch, method, properties, body):
    try:
        log = json.loads(body)
        print(f"Log from {log['source']} received: {log['message']}")
        write_log_to_file(log)
    except Exception as e:
        print(f"Error: {e}")

def start_file_consumer(rabbit_host):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue='logs', durable=True)
    channel.basic_consume(queue='logs', on_message_callback=file_consumer_callback, auto_ack=True)
    print("Writing logs to files. CTRL+C to stop.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()


# [5] RabbitMQ 소비자 - Elasticsearch 전송용

from elasticsearch import Elasticsearch

es = Elasticsearch("http://192.168.10.200:9200")

def es_consumer_callback(ch, method, properties, body):
    try:
        log = json.loads(body)
        index_name = f"{log['source']}-{datetime.now().strftime('%Y-%m-%d')}"
        es.index(index=index_name, document=log)
        print(f"ES Indexed: {log['source']} to {index_name}")
    except Exception as e:
        print(f"ES Error: {e}")

def start_es_consumer(rabbit_host):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbit_host))
    channel = connection.channel()
    channel.queue_declare(queue='logs', durable=True)
    channel.basic_consume(queue='logs', on_message_callback=es_consumer_callback, auto_ack=True)
    print("Sending logs to Elasticsearch. CTRL+C to stop.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
