import os
from ingestion.pipeline import load_and_chunk
from embedding.embedding import embed_and_store, load_vectorstore
from retrieval.retriever import get_retriever
from generation.generation import generation
from config.loader import vectorstore_path


prompt = (
    "You are an assistant for question-answering tasks. "
    "If you don't know the answer, say that you don't know. "
    "use only the provided context to answer."
    "Do not guess, use outside knowledge, or web information."
    "If applicable, cite sources as (source: page) using the metadata"
    "Context: \n{context}\n\n"
    "Question: {question}"
)

if not os.path.exists(vectorstore_path):
    chunks = load_and_chunk()
    vs = embed_and_store(chunks)
else:
    vs = load_vectorstore()
question = input("Question: ")
retrieve = get_retriever(vs)
print(generation(retrieve, prompt, question))




