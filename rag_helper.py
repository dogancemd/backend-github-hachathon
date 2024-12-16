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
from langchain_core.documents import Document

# import pytesseract
# # Set Tesseract OCR executable path if needed
# pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"
# os.environ["OCR_AGENT"] = "tesseract"


model_size = "large-v3"

model = WhisperModel(model_size, device="cuda", compute_type="float16")
#model = WhisperModel(model_size, device="cpu")

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
    print("Loading pdfs:", pdf_list)
    for pdf_path in pdf_list:
        pdf_path = os.path.join(UPLOAD_FOLDER,profile,pdf_path)
        if(os.path.exists(pdf_path+".pkl")):
            print("Loading pickled file")
            with open(pdf_path+".pkl", "rb") as f:
                docs.append(pickle.load(f)[0])
            continue
        loader = UnstructuredPDFLoader(
        file_path=os.path.abspath(pdf_path),
        strategy="hi_res",
        )
        for doc in loader.load_and_split(text_splitter=text_splitter):
            docs.append(Document(doc.page_content, metadata={"title": os.path.basename(pdf_path)}))
        #pickle the file
        with open(pdf_path+".pkl", "wb") as f:
            pickle.dump(docs, f)
    if(profile not in vectorstores):
        vector_store = InMemoryVectorStore.from_documents(docs, OllamaEmbeddings(model="mxbai-embed-large"))
        vectorstores[profile] = vector_store
    else:
        print("Adding doc for profile, doc:", profile, docs)
        vector_store = vectorstores[profile]
        InMemoryVectorStore.add_documents(vector_store, docs)

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
    documents = []
    if not os.path.exists(os.path.join(UPLOAD_FOLDER,profile)):
        os.makedirs(os.path.join(UPLOAD_FOLDER,profile))
    for voice in voice_list:
        #check if the text file exists
        if(os.path.exists(os.path.join(UPLOAD_FOLDER,profile,f"{os.path.basename(voice)}.pkl"))):
            print("Pickle file exists")
            with open(os.path.join(UPLOAD_FOLDER,profile,f"{os.path.basename(voice)}.pkl"), "rb") as f:
                prev_documents = pickle.load(f)
                print("Previous documents:", prev_documents)
                documents.append(prev_documents[0])
            continue
        text = transcribe_audio(os.path.join(UPLOAD_FOLDER,profile,voice))
        #save the text to data/voice_name.txt
        print("Transcribed text:", text)
        splitted = text_splitter.split_text(text)
        for i, split in enumerate(splitted):
            documents.append(Document(split, metadata={"title":f"{os.path.basename(voice)}"}))
        #pickle the file
        with open(os.path.join(UPLOAD_FOLDER,profile,f"{os.path.basename(voice)}.pkl"), "wb") as f:
            pickle.dump(documents, f)
    print("Documents:", documents)
    print("Profile:", profile)
    if(profile not in vectorstores):
        vector_store = InMemoryVectorStore.from_documents(documents, OllamaEmbeddings(model="mxbai-embed-large"))
        vectorstores[profile] = vector_store
    else:
        vector_store = getVectorStore(profile)
        if (type(vector_store) == list):
            vector_store = vector_store[0]
        InMemoryVectorStore.add_documents(vector_store, documents)
    



#load_pdfs("profile1", glob.glob("./data/*.pdf"))