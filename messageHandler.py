from fastapi import FastAPI
import aio_pika
import json
from contextlib import asynccontextmanager
from app.models.mongoDBmanager import MongoDBManager
from fastapi.middleware.cors import CORSMiddleware
from rag_helper import load_voices, load_pdfs
from app.models.common import UPLOAD_FOLDER
import os



async def connectRabbitMQ(app):    
    connection = await aio_pika.connect_robust('amqp://localhost',heartbeat=10)
    channel = await connection.channel()
    await channel.declare_queue("answer_queue")
    app.state.conn, app.state.channel = (connection, channel)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connectRabbitMQ(app)
    yield
    app.state.conn.close()

app = FastAPI(lifespan=lifespan)

mongoManager = MongoDBManager("Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows the listed origins to access the API
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


from app.modules.ask.controller import *
from app.modules.chat_history.controller import *
from app.modules.file.controller import *
    

if __name__ == '__main__':
    for profile in os.listdir(UPLOAD_FOLDER):
        print("profiles:", os.listdir(UPLOAD_FOLDER))
        voice_files = []
        pdf_files = []
        for file in os.listdir(os.path.join(UPLOAD_FOLDER, profile)):

            if file.endswith(".mp3"):
                voice_files.append(file)
            elif file.endswith(".pdf"):
                print(file)
                pdf_files.append(file)
    print(pdf_files)
    print("Calling load voices with", profile, voice_files)
    load_voices(profile,voice_files)
    print("Calling load pdfs with", profile, pdf_files)
    load_pdfs(profile, pdf_files)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
