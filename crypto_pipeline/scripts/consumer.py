import websockets
import json
import asyncio
import os
import pika
import psycopg2
import time
time.sleep(1)  # Wait for RabbitMQ and PostgreSQL to be ready


from psycopg2.extras import execute_values
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
# RabbitMQ connection setup
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST"),
        port=int(os.getenv("RABBITMQ_PORT")),
        credentials=pika.PlainCredentials(
            os.getenv("RABBITMQ_USER"),
            os.getenv("RABBITMQ_PASSWORD")
        )
    )

)
channel = connection.channel()
channel.queue_declare(queue='crypto_trades')
# PostgreSQL connection setup
db_connection = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=int(os.getenv("POSTGRES_PORT")),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB")
)
db_connection.autocommit = True
db_cursor = db_connection.cursor()

def consume():
    print("Waiting for messages...")
    while True:
        method_frame, header_frame, body = channel.basic_get(queue='crypto_trades', auto_ack=True)
        if method_frame:
            data = json.loads(body)
            print(f"Received: {data}")
            # Extract relevant fields
            trade_id = data.get('trade_id')
            product_id = data.get('product_id')
            price = data.get('price')
            size = data.get('size')
            side = data.get('side')
            time_str = data.get('time')
            trade_time = datetime.fromisoformat(time_str) if time_str else None
            raw_data = json.dumps(data)
            
            # Insert into PostgreSQL
            insert_query = """
                INSERT INTO bronze.raw_trades (trade_id, product_id, price, size, side, time, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db_cursor.execute(insert_query, (trade_id, product_id, price, size, side, trade_time, raw_data))
        else:
            time.sleep(1)  # Sleep briefly if no message is received

consume()


