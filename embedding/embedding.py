import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.loader import embedding_model, vectorstore_path
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import DistanceStrategy
from dotenv import load_dotenv

load_dotenv()
gemini_API_key = os.getenv("GEMINI_API_KEY")

def embed_and_store(chunks):
    embedding = GoogleGenerativeAIEmbeddings(
        model = embedding_model,
        api_key = gemini_API_key,
    )
    vectorstore = FAISS.from_documents(documents = chunks, embedding = embedding, distance_strategy=DistanceStrategy.COSINE)
    vectorstore.save_local(vectorstore_path)
    return vectorstore

def load_vectorstore():
    embedding = GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        api_key=gemini_API_key,
    )
    return FAISS.load_local(
        vectorstore_path,
        embedding,
        allow_dangerous_deserialization=True,
    )



