from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import base64
from google import genai
from dotenv import load_dotenv
from ingestion.pipeline import load_and_chunk
from embedding.embedding import embed_and_store, load_vectorstore
from generation.generation import generation
from config.loader import vectorstore_path, llm_model
from retrieval.retriever import get_retriever
from typing import Optional


gemini_api_key = os.getenv("GEMINI_API_KEY")
load_dotenv()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name = "static")

if not os.path.exists(vectorstore_path):
    chunks = load_and_chunk()
    vs = embed_and_store(chunks)
else:
    vs = load_vectorstore()
retriever = get_retriever(vs)

client = genai.Client(api_key = gemini_api_key)

prompt = (
    "You are an assistant for question-answering tasks. "
    "If you don't know the answer, say that you don't know. "
    "When answering in English, translate Vietnamese historical terms to English equivalents. "
    "For example: Nam Han = Southern Han dynasty, Ngo Quyen = King Ngo Quyen... "
    "use only the provided context to answer."
    "Do not guess, use outside knowledge, or web information."
    "If applicable, cite sources as (source: page) using the metadata"
    "Answer in the same language as the question. "
    "Context: \n{context}\n\n"
    "Question: {question}"
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    image: Optional[str] = None

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

@app.post("/chat", response_model = ChatResponse)
async def chat(request: ChatRequest):
    question = request.question

    image_keywords = ["hình", "ảnh", "vẽ", "minh họa", "image", "picture", "draw", "show me", "tạo", "generate"]
    wants_image = any(keyword in question.lower() for keyword in image_keywords)

    image_base64 = None

    if wants_image:
        answer = "Tính năng tạo hình ảnh chưa được kích hoạt. Vui lòng hỏi câu hỏi về trận chiến Bạch Đằng."
        try:
            image_response = client.models.generate_image(
                model="imagen-3.0-generate-002",
                prompt=f"Historical Vietnamese battle scene: {question}",
            )
            image_bytes = image_response.generated_images[0].image.image_bytes
            image_base64 = base64.b64encode(image_bytes).decode()
        except Exception as e:
            print(f"Image generation error: {e}")
    else:
        answer = generation(retriever, question, prompt)

    return ChatResponse(answer=answer, image=image_base64)
