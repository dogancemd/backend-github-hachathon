from langchain_groq import ChatGroq
import os
import dotenv
from langchain_community.document_loaders import UnstructuredPDFLoader
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from typing_extensions import TypedDict
from typing import Annotated, List, Sequence, Tuple
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, AIMessageChunk, BaseMessage, trim_messages
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
import asyncio
import rag_helper

dotenv.load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#using cloud provider for development convenience, llama3.3 can be used fully locally
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
)

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    similar_docs: List[Document]

graph_builder = StateGraph(State)

def need_rag(state: State):
    return len(state["similar_docs"]) > 0

def process_context(documents):
    return "\n".join([doc[0].page_content for doc in documents])

async def rag(state: State):
    prompt = PromptTemplate.from_template("""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.

    Question: {question} 

    Context: {context} 

    Answer:""")
    state["messages"] = trim_messages(state["messages"], strategy="last", token_counter=ChatGroq(model="llama-3.3-70b-versatile"), max_tokens=45)
    answer = await llm.ainvoke(prompt.invoke({"question": state["messages"][-1].content, "context": process_context(state["similar_docs"])}))
    return {"messages": answer}

async def chatbot(state: State):
    prompt = PromptTemplate.from_template("""You are a helpful assistant. Provide a helpful response to the user's question.
    Question: {question}""")
    state["messages"] = trim_messages(state["messages"], strategy="last", token_counter=ChatGroq(model="llama-3.3-70b-versatile"), max_tokens=45)
    answer = await llm.ainvoke(prompt.invoke({"question": state["messages"][-1].content}))
    return {"messages": answer}

graph_builder.add_node("rag", rag)
graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge("chatbot", END)
graph_builder.add_edge("rag", END)

graph_builder.add_conditional_edges(START, need_rag, {True: "rag", False: "chatbot"})

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)  

async def stream_graph_updates(user_input: str, total_user_messages: int, prevMessages: List[Tuple[bool, str]], profile: str):
    config = {"configurable": {"thread_id": "1"}}
    # messages = []
    # for message in prevMessages:
    #     if message[0]:
    #         messages.append(HumanMessage(message[1]))
    #     else:
    #         messages.append(AIMessage(message[1]))
    # messages.append(HumanMessage(user_input))
    # print(messages)
    messages = [HumanMessage(user_input)]
    inputs = {"messages": messages, "similar_docs": rag_helper.get_similar_documents(profile, user_input)}
    print(inputs)
    first = True
    total_current_messages = 0
    async for msg, meta in graph.astream(inputs, config=config, stream_mode="messages"):
        if msg.content and not isinstance(msg, HumanMessage):
            # if(total_user_messages == total_current_messages):
            #     print(msg.content, end="", flush=True)
            # else:
            #     total_current_messages += 1
            yield msg.content

        if isinstance(msg, AIMessageChunk):
            if first:
                gathered = msg
                first = False
            else:
                gathered = gathered + msg

            if msg.tool_call_chunks:
                print(gathered.tool_calls)

async def main():
    total_user_messages = 0
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        await stream_graph_updates(user_input, total_user_messages)
        total_user_messages += 1
        print("\n")

if __name__ == "__main__":
    asyncio.run(main())

#node 1: get similar docs -> if relevant docs then go rag route if not go chatbot route
#node 2: rag route -> respond with similar docs and history