from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
import glob
import os
import pickle
from langchain_chroma import Chroma
from faster_whisper import WhisperModel
from app.models.common import UPLOAD_FOLDER

model_size = "large-v3"

#model = WhisperModel(model_size, device="cuda", compute_type="float16")
model = WhisperModel(model_size, device="cpu")

def transcribe_audio(audio_path):
    text = ""
    segments, info = model.transcribe(audio_path, beam_size=5)
    for segment in segments:
        text += segment.text + " "
    return text

vectorstores = {}

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
)

def load_pdfs(profile, pdf_list):
    docs = []
    for pdf_path in pdf_list:
        if(os.path.exists(pdf_path+".pkl")):
            print("Loading pickled file")
            with open(pdf_path+".pkl", "rb") as f:
                docs.append(pickle.load(f)[0])
            continue
        loader = UnstructuredPDFLoader(
        infer_table_structure = True,
        file_path=pdf_path,
        strategy="hi_res",
        )
        for doc in loader.load_and_split(text_splitter=text_splitter):
            docs.append(doc)
        #pickle the file
        with open(pdf_path+".pkl", "wb") as f:
            pickle.dump(docs, f)
    vector_store = InMemoryVectorStore.from_documents(docs, OllamaEmbeddings(model="mxbai-embed-large"))
    vectorstores[profile] = vector_store

def load_texts(profile, text_list):
    splitted = []
    print(text_list)
    for text in text_list:        
        splitted.append(text_splitter.split_text(text))
    splitted = [doc[0] for doc in splitted]
    print(splitted)
    vector_store = InMemoryVectorStore.from_texts(splitted, OllamaEmbeddings(model="mxbai-embed-large"))
    vectorstores[profile] = vector_store

def getVectorStore(profile:str):
    print(vectorstores)
    if(profile not in vectorstores):
        print("Profile not found")
        return None
    return vectorstores[profile]

def get_similar_documents(profile:str, query:str, limit:float = 0.3):
    vector_store : InMemoryVectorStore = getVectorStore(profile)
    if(vector_store is None):
        return []
    docs = vector_store.similarity_search_with_score(query)
    print("Found documents:", docs)
    docs = [doc for doc in docs if doc[1] > limit]
    print("Docs:", docs)
    return docs

def load_voices(profile:str, voice_list):
    print("Loading voices")
    texts = []
    if not os.path.exists(os.path.join(UPLOAD_FOLDER,profile)):
        os.makedirs(os.path.join(UPLOAD_FOLDER,profile))
    for voice in voice_list:
        #check if the text file exists
        if(os.path.exists(os.path.join(UPLOAD_FOLDER,profile,f"{os.path.basename(voice)}.txt"))):
            print("Text file exists")
            with open(os.path.join(UPLOAD_FOLDER,profile,f"{os.path.basename(voice)}.txt"), "r") as f:
                print(f"Reading text file {os.path.join(UPLOAD_FOLDER,profile,f'{os.path.basename(voice)}.txt')}")
                texts.append(f.read())
                print(texts)
            continue
        text = transcribe_audio(os.path.join(UPLOAD_FOLDER,profile,voice))
        #save the text to data/voice_name.txt
        with open(os.path.join(UPLOAD_FOLDER,profile,f"{os.path.basename(voice)}.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    load_texts(profile, texts)


#load_pdfs("profile1", glob.glob("./data/*.pdf"))