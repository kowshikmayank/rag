import hashlib
import json
import os
import uuid
from typing import List

import openai
from flask import Response
from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document, StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain_core.runnables import RunnablePassthrough
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http.models import (Distance, FieldCondition, Filter,
                                       MatchValue, PointStruct, UpdateStatus,
                                       VectorParams)


def process_pdf(path: str):
    with open(path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() 
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1500,
        chunk_overlap=250,
    )
    docs = text_splitter.create_documents([p.extract_text() for p in reader.pages])
    chunks = list()
    for doc in docs:
        chunks.append(
            {
                "text": doc.dict()["page_content"],
                "document": os.path.basename(path),
                "hash": file_hash,
            }
        )
    return chunks


class QdrantVectorStore:

    def __init__(self,
                 host: str = "vectordb",
                 port: int = 6333,
                 collection_name: str = "test_collection",
                 vector_size: int = 1536,
                 vector_distance=Distance.COSINE
                 ):

        self.client = QdrantClient(
            url=host,
            port=port,
        )
        self.collection_name = collection_name
        
        self.openai_client = openai.OpenAI()
        
        try:
            self.client.get_collection(collection_name=collection_name)
        except Exception as e:
            print("Collection does not exist, creating collection now")
            self.set_up_collection(collection_name,  vector_size, vector_distance)
        
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="document",
            field_schema="keyword",
        )


    def set_up_collection(self, collection_name: str, vector_size: int, vector_distance: str):

        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=vector_distance)
        )

    def upsert_data(self, data: List[dict]):
        points = []
        for item in data:
            text = item.get("text")
            document = item.get("document")
            hash = item.get("hash")
            text_vector = self.openai_client.embeddings.create(input=text,model="text-embedding-ada-002").data[0].embedding
            text_id = str(uuid.uuid4())
            payload = {"text": text, "document": document, "hash": hash}
            point = PointStruct(id=text_id, vector=text_vector, payload=payload)
            points.append(point)

        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=points)

        if operation_info.status == UpdateStatus.COMPLETED:
            print("Data inserted successfully!")
        else:
            print("Failed to insert data")


    def search_with_filter(self, input_query: str, filter: list, limit: int = 3):
        input_vector = self.openai_client.embeddings.create(input=input_query,model="text-embedding-ada-002").data[0].embedding

        filter_list = []
        for f in filter:
            filter_list.append(
                FieldCondition(key="document", match=MatchValue(value=f))
            )

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=input_vector,
            query_filter=Filter(
                should=filter_list
            ),
            limit=limit
        )

        result = []
        for item in search_result:
            similarity_score = item.score
            payload = item.payload
            data = {"id": item.id, "similarity_score": similarity_score, "text": payload.get("text"),
                    "document": payload.get("document"), "hash": payload.get("hash")}
            result.append(data)

        return result
    

def return_error(message, e, statuscode):
    body = {"Error": f"{message}: {e}"}
    
    return Response(
        response=json.dumps(body),
        status=statuscode,
        mimetype="application/json",
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def qa_pipeline(query:str,results:list):
    
    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    # Creating a local vector store in case we want to play around with retrieved result treatment 
    qdrant = Qdrant.from_documents(
    [Document(page_content=r.get("text"), metadata={"source": "local"}) for r in results],
    embedding = OpenAIEmbeddings(),
    location=":memory:",  # Local mode with in-memory storage only
    collection_name="local",
    )
    retriever = qdrant.as_retriever(search_kwargs={'k': 3}) 
    rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
    )
    return rag_chain.invoke(query)

