import websockets
import json
import asyncio
import os
import pika
from dotenv import load_dotenv

load_dotenv()

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



subscribe_message = {
    "type": "subscribe",
    "product_ids": ["BTC-USD", "ETH-USD", "SOL-USD"],
    "channels": ["matches"]
}


async def produce():
    print("Connecting to WebSocket...")
    uri = "wss://ws-feed.exchange.coinbase.com"
    async with websockets.connect(uri) as websocket:
        print("WebSocket connected!")
        await websocket.send(json.dumps(subscribe_message))
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Sent: {data}")
            channel.basic_publish(
                exchange='', 
                routing_key='crypto_trades', 
                body=json.dumps(data)
            )

import time

async def main():
    while True:
        try:
            await produce()
        except Exception as e:
            print(f"Connection dropped: {e}, reconnecting in 5 seconds...")
            await asyncio.sleep(5)

asyncio.run(main())





