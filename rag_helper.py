from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
import glob
import os
import pickle
from langchain_chroma import Chroma
from faster_whisper import WhisperModel

model_size = "large-v3"

model = WhisperModel(model_size, device="cuda", compute_type="float16")

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
    for text_path in text_list:        
        with open(text_path, "r") as f:
            text = f.read()
            splitted += text_splitter.split_text(text)
    vector_store = InMemoryVectorStore.from_texts(splitted, OllamaEmbeddings(model="mxbai-embed-large"))
    vectorstores[profile] = vector_store

def getVectorStore(profile:str):
    return vectorstores[profile]

def get_similar_documents(profile:str, query:str, limit:int = 0.5):
    vector_store : InMemoryVectorStore = getVectorStore(profile)
    docs = vector_store.similarity_search_with_score(query)
    docs = [doc for doc in docs if doc[1] > limit]
    return docs

def load_voices(profile:str, voice_list):
    texts = []
    if not os.path.exists("./files/"+profile+"/"):
        os.makedirs("./files/"+profile)
    for voice in voice_list:
        text = transcribe_audio(voice)
        #save the text to data/voice_name.txt
        with open("./files/"+profile+ "/" +os.path.basename(voice)+".txt", "w") as f:
            f.write(text)
    
    texts = glob.glob("./files/"+profile+"/*.txt")
    load_texts(profile, texts)


#load_pdfs("profile1", glob.glob("./data/*.pdf"))
load_voices("profile1", glob.glob("./voices/profile1/*.mp3"))
load_voices("sagopa", glob.glob("./voices/sabahattin/*.mp3"))