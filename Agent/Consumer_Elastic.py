from elasticsearch import Elasticsearch
import pika
import json
from datetime import datetime

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
