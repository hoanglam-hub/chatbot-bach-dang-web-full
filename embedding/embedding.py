import os
from langchain_openai import OpenAIEmbeddings
from config.loader import embedding_model, vectorstore_path
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from dotenv import load_dotenv

load_dotenv()
openAI_API_key = os.getenv("OPENAI_API_KEY")

def embed_and_store(chunks):
    embedding = OpenAIEmbeddings(
        model = embedding_model,
        api_key = openAI_API_key,
    )
    vectorstore = FAISS.from_documents(documents = chunks, embedding = embedding, distance_strategy=DistanceStrategy.COSINE)
    vectorstore.save_local(vectorstore_path)
    return vectorstore

def load_vectorstore():
    embedding = OpenAIEmbeddings(
        model=embedding_model,
        api_key=openAI_API_key,
    )
    return FAISS.load_local(
        vectorstore_path,
        embedding,
        allow_dangerous_deserialization=True,
    )



