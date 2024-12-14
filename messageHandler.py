from fastapi import FastAPI
from app.modules.ask.helper import askHelper
from app.modules.ask.schema import AskRequest
import aio_pika
import json
from contextlib import asynccontextmanager



async def connectRabbitMQ(app):    
    connection = await aio_pika.connect_robust('amqp://localhost',heartbeat=10)
    channel = await connection.channel()
    channel.declare_queue("answer_queue")
    app.state.conn, app.state.channel = (connection, channel)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connectRabbitMQ(app)
    yield
    app.state.conn.close()

app = FastAPI(lifespan=lifespan)

from app.modules.ask.controller import *
from app.modules.chat_history.controller import *
    


