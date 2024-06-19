from fastapi import FastAPI
from langchain_cohere import ChatCohere
from langchain_community.document_loaders import WebBaseLoader
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain.pydantic_v1 import BaseModel
from langserve import add_routes
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers.string import StrOutputParser

import pandas as pd
import requests

with open("data.csv", "w") as f:
    r = requests.get("https://docs.google.com/spreadsheets/u/7/d/1JNgL-tDuU_R6BjvBgEzUjTJwEDTpqv3zK08KZ6Ab85Q/export?format=csv&id=1JNgL-tDuU_R6BjvBgEzUjTJwEDTpqv3zK08KZ6Ab85Q&gid=1175330818")
    f.write(r.text)

df = pd.read_csv("data.csv")
links = df['Link'].dropna().tolist()

from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader(links, requests_per_second=100, verify_ssl=False)
documents = loader.aload()

embeddings = CohereEmbeddings()
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()


llm = ChatCohere()
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_context(input):
    return input['question']


rag_chain = (
    RunnableLambda(get_context)
    | {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API server using LangChain's Runnable interfaces",
)


class Input(BaseModel): 
    question: str


class Output(BaseModel):
    output: str


add_routes(
    app,
    rag_chain.with_types(input_type=Input, output_type=Output),
    path="/agent",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
