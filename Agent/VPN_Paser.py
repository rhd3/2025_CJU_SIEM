import json
import pika
import os
import time
from datetime import datetime

RABBITMQ_HOST = "192.168.10.100"

def tail_file(filepath):
    with open(filepath, 'r') as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                yield line

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

def send_to_rabbitmq(entry):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue='logs', durable=True)
    channel.basic_publish(exchange='', routing_key='logs', body=json.dumps(entry))
    connection.close()