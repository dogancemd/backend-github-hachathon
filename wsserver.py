

"""Echo server using the asyncio API."""
import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed
import json
import pika
import threading


sockets = set()

async def websocket_handler(websocket):
    sockets.add(websocket)
    print("Client connected")
    try:
        # Keep the connection open
        async for message in websocket:
            print(message)
            await websocket.send(message)
    except ConnectionClosed:
        print("Client disconnected")
    finally:
        sockets.remove(websocket)


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)




async def produce(body):
    print("Producing")
    for socket in sockets:
        await socket.send(body)


def callback(ch, method, properties, body):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(produce(body))

def callback_test(ch, method, properties, body):
    print(body)


def rabbitMQ_start():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='answer_queue')
    channel.basic_consume(queue='answer_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

async def webSocketServer():
    async with serve(websocket_handler, "0.0.0.0", 8765) as server:
        await server.serve_forever()

def startWebsocketServer():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(webSocketServer())

async def main():
    websocketThread = threading.Thread(target=startWebsocketServer)
    rabbitMQThread = threading.Thread(target=rabbitMQ_start)
    rabbitMQThread.start()
    websocketThread.start()
    websocketThread.join()
    rabbitMQThread.join()


if __name__ == "__main__":
    print("Started")
    asyncio.run(main())
    print("Stopped")
